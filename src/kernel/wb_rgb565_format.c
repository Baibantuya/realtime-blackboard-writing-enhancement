// Format-only media subdev for the combinational PL formatter. No pixel buffers
// or capture scheduler: original Xilinx VIPP and framebuffer DMA retain control.
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/mutex.h>
#include <media/v4l2-async.h>
#include <media/v4l2-subdev.h>
#include <media/media-entity.h>

struct wb_format {
    struct v4l2_subdev sd;
    struct media_pad pads[2];
    struct v4l2_mbus_framefmt fmt[2];
    struct mutex lock;
    bool streaming;
};
static struct wb_format *to_format(struct v4l2_subdev *sd)
{ return container_of(sd,struct wb_format,sd); }
static u32 pad_code(unsigned int pad)
{ return pad ? MEDIA_BUS_FMT_UYVY8_1X16 : MEDIA_BUS_FMT_RBG888_1X24; }
static void default_fmt(struct v4l2_mbus_framefmt *f,unsigned int pad)
{
    memset(f,0,sizeof(*f));f->width=1920;f->height=1080;f->code=pad_code(pad);
    f->field=V4L2_FIELD_NONE;f->colorspace=V4L2_COLORSPACE_SRGB;
}
static int init_cfg(struct v4l2_subdev *sd,struct v4l2_subdev_state *cfg)
{
    unsigned int p;
    for(p=0;p<2;p++) default_fmt(v4l2_subdev_get_try_format(sd,cfg,p),p);
    return 0;
}
static int enum_code(struct v4l2_subdev *sd,struct v4l2_subdev_state *cfg,
                     struct v4l2_subdev_mbus_code_enum *code)
{
    if(code->pad>1 || code->index)return -EINVAL;
    code->code=pad_code(code->pad);return 0;
}
static int get_fmt(struct v4l2_subdev *sd,struct v4l2_subdev_state *cfg,
                   struct v4l2_subdev_format *f)
{
    struct wb_format *c=to_format(sd);
    if(f->pad>1)return -EINVAL;
    mutex_lock(&c->lock);
    f->format=f->which==V4L2_SUBDEV_FORMAT_TRY ?
        *v4l2_subdev_get_try_format(sd,cfg,f->pad) : c->fmt[f->pad];
    mutex_unlock(&c->lock);return 0;
}
static int set_fmt(struct v4l2_subdev *sd,struct v4l2_subdev_state *cfg,
                   struct v4l2_subdev_format *f)
{
    struct wb_format *c=to_format(sd);unsigned int p;
    if(f->pad>1)return -EINVAL;
    mutex_lock(&c->lock);
    if(c->streaming && f->which==V4L2_SUBDEV_FORMAT_ACTIVE){mutex_unlock(&c->lock);return -EBUSY;}
    f->format.width=clamp_t(u32,f->format.width,64,1920)&~1u;
    f->format.height=clamp_t(u32,f->format.height,1,1080);
    f->format.code=pad_code(f->pad);f->format.field=V4L2_FIELD_NONE;
    f->format.colorspace=V4L2_COLORSPACE_SRGB;
    for(p=0;p<2;p++) {
        struct v4l2_mbus_framefmt *target=f->which==V4L2_SUBDEV_FORMAT_TRY ?
            v4l2_subdev_get_try_format(sd,cfg,p) : &c->fmt[p];
        *target=f->format;target->code=pad_code(p);
    }
    mutex_unlock(&c->lock);return 0;
}
static int stream(struct v4l2_subdev *sd,int enable)
{
    struct wb_format *c=to_format(sd);
    mutex_lock(&c->lock);c->streaming=!!enable;mutex_unlock(&c->lock);
    return 0; // Wire conversion is always live; no AP_START and no MMIO.
}
static const struct v4l2_subdev_pad_ops pads={.init_cfg=init_cfg,.enum_mbus_code=enum_code,.get_fmt=get_fmt,.set_fmt=set_fmt};
static const struct v4l2_subdev_video_ops video={.s_stream=stream};
static const struct v4l2_subdev_ops ops={.pad=&pads,.video=&video};
static int probe(struct platform_device *pdev)
{
    struct wb_format *c;int rc;unsigned int p;
    c=devm_kzalloc(&pdev->dev,sizeof(*c),GFP_KERNEL);if(!c)return -ENOMEM;
    mutex_init(&c->lock);v4l2_subdev_init(&c->sd,&ops);
    c->sd.owner=THIS_MODULE;c->sd.dev=&pdev->dev;c->sd.fwnode=dev_fwnode(&pdev->dev);
    c->sd.flags|=V4L2_SUBDEV_FL_HAS_DEVNODE;
    strscpy(c->sd.name,"rgb565_format_adapter",sizeof(c->sd.name));
    c->sd.entity.function=MEDIA_ENT_F_PROC_VIDEO_PIXEL_FORMATTER;
    c->pads[0].flags=MEDIA_PAD_FL_SINK;c->pads[1].flags=MEDIA_PAD_FL_SOURCE;
    for(p=0;p<2;p++)default_fmt(&c->fmt[p],p);
    rc=media_entity_pads_init(&c->sd.entity,2,c->pads);if(rc)return rc;
    platform_set_drvdata(pdev,c);rc=v4l2_async_register_subdev(&c->sd);
    if(rc)media_entity_cleanup(&c->sd.entity);
    return rc;
}
static int remove_format(struct platform_device *pdev)
{
    struct wb_format *c=platform_get_drvdata(pdev);
    v4l2_async_unregister_subdev(&c->sd);media_entity_cleanup(&c->sd.entity);return 0;
}
static const struct of_device_id match[]={ {.compatible="whiteboard,rgb565-format-1.0"},{} };
MODULE_DEVICE_TABLE(of,match);
static struct platform_driver wb_format_driver={.probe=probe,.remove=remove_format,
    .driver={.name="wb-rgb565-format",.of_match_table=match}};
module_platform_driver(wb_format_driver);
MODULE_LICENSE("GPL");MODULE_VERSION("1.0");
MODULE_DESCRIPTION("Format-only RGB565 byte carrier subdev; original vendor DMA owns capture");
