// SPDX-License-Identifier: GPL-2.0
// Low-DDR DMA-BUF frame exporter for the actual HP0 rectifier device.
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/of.h>
#include <linux/dma-mapping.h>
#include <linux/dma-map-ops.h>
#include <linux/dma-buf.h>
#include <linux/dma-buf-map.h>
#include <linux/scatterlist.h>
#include <linux/miscdevice.h>
#include <linux/fs.h>
#include <linux/file.h>
#include <linux/uaccess.h>
#include <linux/slab.h>
#include <linux/io.h>
#include <linux/delay.h>
#include <linux/iommu.h>
#include <linux/mutex.h>

#define WB_ABI 6
#define WB_LIMIT 0x80000000ULL
#define WB_ATTRS (DMA_ATTR_FORCE_CONTIGUOUS | DMA_ATTR_WRITE_COMBINE)
struct wb_request { __u64 size, dma_address; __s32 fd; __u32 reserved; };
#define WB_ALLOC _IOWR('W',0x40,struct wb_request)
#define WB_START _IOW('W',0x41,__s32)
#define WB_DONE  _IOW('W',0x42,__s32)
#define WB_VERSION _IOR('W',0x43,__u32)
#define WB_QUANT_START _IOW('W',0x44,__s32)
#define WB_QUANT_DONE _IOW('W',0x45,__s32)
#define WB_CAPTURE_START _IOW('W',0x46,__s32)
#define WB_CAPTURE_DONE _IOW('W',0x47,__s32)
struct wb_pool { struct device *dev; void __iomem *ctrl; void __iomem *quant_ctrl; void __iomem *capture_ctrl; struct miscdevice misc;
    atomic_t buffers, users; bool online; };
struct wb_buffer { struct wb_pool *pool; void *cpu; dma_addr_t dma; size_t size;
    struct mutex lock; unsigned int pl_active; };

static bool idle(struct wb_pool *p) { return !!(readl(p->ctrl)&4); }
static struct sg_table *map_buffer(struct dma_buf_attachment *a,enum dma_data_direction dir) {
    struct wb_buffer *b=a->dmabuf->priv; struct sg_table *sgt;
    struct scatterlist *sg; dma_addr_t next; size_t total=0; int i,n,rc;
    // HP0 is a physical DDR master. Reject translation/bounce aliases rather
    // than silently creating a copy hidden behind a different DMA address.
    if(iommu_get_domain_for_dev(a->dev)) return ERR_PTR(-EOPNOTSUPP);
    sgt=kzalloc(sizeof(*sgt),GFP_KERNEL); if(!sgt)return ERR_PTR(-ENOMEM);
    rc=dma_get_sgtable_attrs(b->pool->dev,sgt,b->cpu,b->dma,b->size,WB_ATTRS);
    if(rc) { kfree(sgt);return ERR_PTR(rc); }
    n=dma_map_sg(a->dev,sgt->sgl,sgt->orig_nents,dir);
    if(!n) { rc=-EIO;goto fail; }
    sgt->nents=n; next=b->dma;
    for_each_sg(sgt->sgl,sg,n,i) {
        if(sg_dma_address(sg)!=next) { rc=-ERANGE;goto unmap; }
        total+=sg_dma_len(sg);next+=sg_dma_len(sg);
    }
    if(total<b->size || next>WB_LIMIT) {rc=-ERANGE;goto unmap;}
    pr_info("wb_frame_pool: DMA-BUF import %s nents=%d addr=%pad bytes=%zu\n",dev_name(a->dev),n,&b->dma,total);
    return sgt;
unmap:
    dma_unmap_sg(a->dev,sgt->sgl,sgt->orig_nents,dir);
fail:
    sg_free_table(sgt);kfree(sgt);return ERR_PTR(rc);
}
static void unmap_buffer(struct dma_buf_attachment *a,struct sg_table *sgt,enum dma_data_direction dir) {
    dma_unmap_sg(a->dev,sgt->sgl,sgt->orig_nents,dir);sg_free_table(sgt);kfree(sgt);
}
static int map_cpu(struct dma_buf *db,struct vm_area_struct *vma) {
    struct wb_buffer *b=db->priv;
    if((vma->vm_end-vma->vm_start)+(vma->vm_pgoff<<PAGE_SHIFT)>b->size)return -EINVAL;
    return dma_mmap_attrs(b->pool->dev,vma,b->cpu,b->dma,b->size,WB_ATTRS);
}
static int cpu_access(struct dma_buf *db,enum dma_data_direction dir) {
    struct wb_buffer *b=db->priv;
    // dma_mmap_attrs of this non-coherent device is write-combined/uncached.
    // CPU accesses are read-only in the supplied runtime and need no copy.
    if(dir!=DMA_FROM_DEVICE && dir!=DMA_TO_DEVICE && dir!=DMA_BIDIRECTIONAL)return -EPERM;
    if(READ_ONCE(b->pl_active))return -EBUSY;
    dma_rmb();
    return 0;
}
static void release_buffer(struct dma_buf *db) {
    struct wb_buffer *b=db->priv;struct wb_pool *p=b->pool;
    // SIGKILL/exception must not free a source still being read by PL.
    while(((READ_ONCE(b->pl_active)&1) && !idle(p)) ||
          ((READ_ONCE(b->pl_active)&2) && !(readl(p->quant_ctrl)&4)) ||
          ((READ_ONCE(b->pl_active)&4) && !(readl(p->capture_ctrl)&4)))msleep(10);
    dma_free_attrs(p->dev,b->size,b->cpu,b->dma,WB_ATTRS);
    atomic_dec(&p->buffers);kfree(b);
}
static int map_kernel(struct dma_buf *db,struct dma_buf_map *map) {
    struct wb_buffer *b=db->priv;
    dma_buf_map_set_vaddr(map,b->cpu);return 0;
}
static void unmap_kernel(struct dma_buf *db,struct dma_buf_map *map) { }
static const struct dma_buf_ops buffer_ops={
    .map_dma_buf=map_buffer,.unmap_dma_buf=unmap_buffer,.mmap=map_cpu,
    .begin_cpu_access=cpu_access,.end_cpu_access=cpu_access,.release=release_buffer,
    .vmap=map_kernel,.vunmap=unmap_kernel,
};
static long allocate(struct wb_pool *p,void __user *arg) {
    struct wb_request r;struct wb_buffer *b;struct dma_buf *db;int fd;
    DEFINE_DMA_BUF_EXPORT_INFO(e);
    if(copy_from_user(&r,arg,sizeof(r)))return -EFAULT;
    if(r.reserved || r.size<4096 || r.size>32*1024*1024)return -EINVAL;
    b=kzalloc(sizeof(*b),GFP_KERNEL);if(!b)return -ENOMEM;
    b->pool=p;b->size=PAGE_ALIGN(r.size);mutex_init(&b->lock);
    b->cpu=dma_alloc_attrs(p->dev,b->size,&b->dma,GFP_KERNEL,WB_ATTRS);
    if(!b->cpu) {kfree(b);return -ENOMEM;}
    if(b->dma+b->size>WB_LIMIT || !IS_ALIGNED(b->dma,64)) {
        dma_free_attrs(p->dev,b->size,b->cpu,b->dma,WB_ATTRS);kfree(b);return -ERANGE;
    }
    memset(b->cpu,0,b->size);
    e.ops=&buffer_ops;e.size=b->size;e.flags=O_RDWR;e.priv=b;e.exp_name="wb-frame-pool-v4";
    atomic_inc(&p->buffers);db=dma_buf_export(&e);
    if(IS_ERR(db)) {release_buffer((struct dma_buf *)&(struct dma_buf){.priv=b});return PTR_ERR(db);}
    fd=get_unused_fd_flags(O_CLOEXEC);if(fd<0) {dma_buf_put(db);return fd;}
    r.size=b->size;r.dma_address=b->dma;r.fd=fd;
    if(copy_to_user(arg,&r,sizeof(r))) {put_unused_fd(fd);dma_buf_put(db);return -EFAULT;}
    fd_install(fd,db->file);return 0;
}
static long pool_ioctl(struct file *f,unsigned int cmd,unsigned long arg) {
    struct wb_pool *p=f->private_data;void __user *u=(void __user *)arg;
    struct dma_buf *db;struct wb_buffer *b;int fd,rc=0;__u32 version=WB_ABI;
    if(!READ_ONCE(p->online))return -ENODEV;
    if(cmd==WB_VERSION)return copy_to_user(u,&version,sizeof(version))?-EFAULT:0;
    if(cmd==WB_ALLOC)return allocate(p,u);
    if(cmd!=WB_START && cmd!=WB_DONE && cmd!=WB_QUANT_START && cmd!=WB_QUANT_DONE &&
       cmd!=WB_CAPTURE_START && cmd!=WB_CAPTURE_DONE)return -ENOTTY;
    if(copy_from_user(&fd,u,sizeof(fd)))return -EFAULT;
    db=dma_buf_get(fd);if(IS_ERR(db))return PTR_ERR(db);
    if(db->ops!=&buffer_ops || ((struct wb_buffer *)db->priv)->pool!=p) {rc=-EINVAL;goto out;}
    b=db->priv;mutex_lock(&b->lock);
    if(cmd==WB_CAPTURE_START || cmd==WB_CAPTURE_DONE) {
        if(!(readl(p->capture_ctrl)&4))rc=-EBUSY;
        else if(cmd==WB_CAPTURE_START) {
            if(b->pl_active)rc=-EBUSY;else WRITE_ONCE(b->pl_active,4);
        } else WRITE_ONCE(b->pl_active,b->pl_active&~4u);
    } else if(cmd==WB_QUANT_START || cmd==WB_QUANT_DONE) {
        if(!(readl(p->quant_ctrl)&4))rc=-EBUSY;
        else if(cmd==WB_QUANT_START) {
            if(b->pl_active)rc=-EBUSY;else WRITE_ONCE(b->pl_active,2);
        } else WRITE_ONCE(b->pl_active,b->pl_active&~2u);
    } else if(!idle(p))rc=-EBUSY;
    else if(cmd==WB_START) {
        if(b->pl_active)rc=-EBUSY;else WRITE_ONCE(b->pl_active,1);
    } else WRITE_ONCE(b->pl_active,b->pl_active&~1u);
    mutex_unlock(&b->lock);
out:
    dma_buf_put(db);return rc;
}
static int pool_open(struct inode *i,struct file *f) {
    struct wb_pool *p=container_of(f->private_data,struct wb_pool,misc);
    if(!READ_ONCE(p->online))return -ENODEV;
    atomic_inc(&p->users);f->private_data=p;return 0;
}
static int pool_close(struct inode *i,struct file *f) {
    struct wb_pool *p=f->private_data;atomic_dec(&p->users);return 0;
}
static const struct file_operations pool_fops={.owner=THIS_MODULE,.open=pool_open,
    .release=pool_close,.unlocked_ioctl=pool_ioctl,.compat_ioctl=pool_ioctl};
static int pool_probe(struct platform_device *pdev) {
    struct wb_pool *p;struct resource *r;int rc;
    if(iommu_get_domain_for_dev(&pdev->dev) || dev_is_dma_coherent(&pdev->dev))return -EOPNOTSUPP;
    if(!pdev->dev.dma_mask)pdev->dev.dma_mask=&pdev->dev.coherent_dma_mask;
    // ARM64's DMA zone support requires a 32-bit mask. The allocation and
    // mapping checks above independently enforce the actual <2 GiB HP0 window.
    rc=dma_set_mask_and_coherent(&pdev->dev,DMA_BIT_MASK(32));if(rc)return rc;
    p=devm_kzalloc(&pdev->dev,sizeof(*p),GFP_KERNEL);if(!p)return -ENOMEM;
    r=platform_get_resource(pdev,IORESOURCE_MEM,0);
    if(!r || r->start!=0x80040000 || resource_size(r)<0x10000)return -EINVAL;
    p->ctrl=devm_ioremap_resource(&pdev->dev,r);if(IS_ERR(p->ctrl))return PTR_ERR(p->ctrl);
    // Diagnostic prototype may reuse the v4 DT node; final v6 node includes
    // the quantizer resource explicitly. Fixed address matches the HWH guard.
    p->quant_ctrl=devm_ioremap(&pdev->dev,0x80060000,0x10000);
    if(!p->quant_ctrl)return -ENOMEM;
    p->capture_ctrl=devm_ioremap(&pdev->dev,0xa0020000,0x10000);
    if(!p->capture_ctrl)return -ENOMEM;
    p->dev=&pdev->dev;atomic_set(&p->buffers,0);atomic_set(&p->users,0);p->online=true;
    p->misc.minor=MISC_DYNAMIC_MINOR;p->misc.name="wb_frame_pool";
    p->misc.fops=&pool_fops;p->misc.parent=&pdev->dev;p->misc.mode=0600;
    platform_set_drvdata(pdev,p);return misc_register(&p->misc);
}
static int pool_remove(struct platform_device *pdev) {
    struct wb_pool *p=platform_get_drvdata(pdev);WRITE_ONCE(p->online,false);
    misc_deregister(&p->misc);
    while(atomic_read(&p->buffers) || atomic_read(&p->users))msleep(10);
    return 0;
}
static const struct of_device_id pool_match[]={{.compatible="whiteboard,shared-rectify-5.0"},{.compatible="whiteboard,shared-rectify-4.0"},{}};
MODULE_DEVICE_TABLE(of,pool_match);
static struct platform_driver pool_driver={.probe=pool_probe,.remove=pool_remove,
    .driver={.name="wb-frame-pool",.of_match_table=pool_match}};
module_platform_driver(pool_driver);
MODULE_LICENSE("GPL");
MODULE_IMPORT_NS(DMA_BUF);
MODULE_DESCRIPTION("Shared low-DDR frame pool with independent rectify/quantize/capture ownership, ABI6");
MODULE_VERSION("6.0");
