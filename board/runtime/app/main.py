"""V24 production entry with optional same-frame diagnostic captures."""
import argparse
import sys
from pathlib import Path
_PACKAGE_ROOT = Path(__file__).resolve().parents[1]
for _part in ('app', 'drivers', 'ui'):
    sys.path.insert(0, str(_PACKAGE_ROOT / _part))
from runtime_paths import DATA
import json
import time
from concurrent.futures import ThreadPoolExecutor


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--runtime',required=True)
    args,extra=parser.parse_known_args()
    runtime=Path(args.runtime).resolve()
    sys.path.insert(0,str(runtime))
    import numpy as np
    import ps_runtime_v2.__main__ as entry
    from ps_runtime_v2.board import BoardIO
    from ps_runtime_v2.scheduler import Stage

    def save(folder,images,record):
        folder.mkdir(parents=True,exist_ok=False)
        for name,values in images.items():
            if name!='identity':np.save(folder/(name+'.npy'),values,allow_pickle=False)
        (folder/'capture.json').write_text(json.dumps(record,indent=2))
        return folder

    class CaptureIO(BoardIO):
        def __init__(self,*a,**kw):
            super().__init__(*a,**kw)
            self.capture=None
            self.capture_writer=ThreadPoolExecutor(max_workers=1)
            self.capture_future=None

        def launch(self,stage,work,now):
            request=DATA/'capture_full.request'
            if self.capture_future is not None and self.capture_future.done():
                folder=self.capture_future.result()
                print(json.dumps(dict(event='same_frame_capture',folder=str(folder))),flush=True)
                self.capture_future=None
            if stage==Stage.RECTIFY and self.capture is None and self.capture_future is None and request.exists():
                request.unlink()
                work.camera.begin_cpu()
                try:raw=np.array(work.camera.frame,copy=True)
                finally:work.camera.end_cpu()
                self.capture=dict(identity=work.key.identity,raw=raw)
            if stage==Stage.QUANTIZE and self.capture is not None and self.capture['identity']==work.key.identity:
                previous=self.quantizer.last_context
                context=self.context(work.key)
                changed=previous is not None and context.epochs!=previous.epochs
                same_coordinates=changed and (context.capture_epoch,context.geometry_epoch)==(previous.capture_epoch,previous.geometry_epoch)
                self.quantizer.canvases[self.quantizer.front].invalidate()
                self.capture['canvas_before']=np.array(self.quantizer.canvases[self.quantizer.front],copy=True)
                # Match the existing launch adapter's epoch handling exactly;
                # the copied input is what Q will read after this host reset.
                if same_coordinates:self.capture['canvas_before']&=np.uint32(0x77777777)
                elif changed:self.capture['canvas_before'][:]=np.uint32(0)  # R6 blank; label 7 is pink.
            super().launch(stage,work,now)

        def poll(self,stage,work,now):
            done=super().poll(stage,work,now)
            if done and self.capture is not None and self.capture['identity']==work.key.identity:
                if stage in (Stage.RECTIFY,Stage.RESTORE):
                    buf=work.a if stage==Stage.RECTIFY else work.b
                    buf.invalidate()
                    self.capture['rectified' if stage==Stage.RECTIFY else 'restored']=np.array(buf,copy=True)
            return done

        def present(self,work,now):
            if self.capture is not None and self.capture['identity']==work.key.identity:
                dst=self.quantizer.destination
                if hasattr(dst,'snapshot'):image=dst.snapshot()
                else:dst.invalidate();image=np.array(dst,copy=True)
                self.capture['quantized']=image
                self.quantizer.metadata.invalidate()
                self.capture['metadata']=np.array(self.quantizer.metadata,copy=True)
                self.quantizer.canvases[self.quantizer.front].invalidate()
                self.capture['canvas_after']=np.array(self.quantizer.canvases[self.quantizer.front],copy=True)
                folder=DATA/'captures'/('frame_%010d'%work.key.sequence)
                record=dict(sequence=work.key.sequence,identity=list(work.key.identity),hold=bool(self.quantizer.hold),
                    captured_at=work.key.captured_at,completed_at=now,
                    transform_version=work.transform.version,
                    corners=work.transform.source_corners.tolist(),target_rect=list(work.transform.target_rect),
                    source_size=list(work.transform.source_size),runtime_report=self.report(now))
                record['q_parameters']=dict(ink_delta=self.quantizer.ink_delta,
                    erase_delta=self.quantizer.erase_delta,
                    color_margin=self.quantizer.color_margin,order=0)
                self.capture_future=self.capture_writer.submit(save,folder,self.capture,record)
                self.capture=None
            super().present(work,now)

        def close(self):
            super().close()
            self.capture_writer.shutdown(wait=True)

    entry.BoardIO=CaptureIO
    sys.argv=[sys.argv[0],'--runtime',str(runtime)]+extra
    entry.main()


if __name__=='__main__':main()
