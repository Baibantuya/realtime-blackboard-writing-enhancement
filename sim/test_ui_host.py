"""Headless Linux UI smoke test. No PYNQ imports, MMIO or board claims."""
from pathlib import Path
import hashlib, json, platform, sys
import numpy as np
from PIL import Image

sys.dont_write_bytecode = True
root = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(root/'src/ps/app'), str(root/'src/ps/ui')]
from archive_ui import NativeUI

out = root/'report/ui_host'
out.mkdir(parents=True, exist_ok=False)
library = root/'build/work/ui/build/libboard_ps_ui.so'
native = NativeUI(library)
checks = []
try:
    assert native.lib.ps_collapsed() == 1
    native.lib.ps_scope(1)
    native.lib.ps_nav(4)
    assert native.lib.ps_collapsed() == 0
    for mode in range(3):
        native.lib.ps_state(mode, 0, 0, 0., 1, 0)
        native.render()
        assert native.patch is not None
        Image.fromarray(native.overlay[:, :, [2, 1, 0, 3]]).save(out/f'mode_{mode}.png')
        checks.append(f'mode_{mode}_render')
    for key in [0xF4, 0xF5]:
        native.lib.ps_key(key)
        assert native.lib.ps_take() == key
    assert native.lib.ps_take() == 0
    native.lib.ps_tick(10001)
    assert native.lib.ps_collapsed() == 1
    native.lib.ps_nav(4); native.lib.ps_nav(5)
    assert native.lib.ps_collapsed() == 1
    checks += ['previous_next_command_queue', 'idle_autohide', 'up_down_navigation']
    # Validate the native RGB565 copy without depending on screen hardware.
    a = np.arange(1920*1080, dtype=np.uint16).reshape(1080,1920)
    b = np.zeros_like(a)
    native.copy(b,a)
    assert np.array_equal(a,b)
    checks.append('rgb565_copy_exact')
finally:
    native.close()
result = {'status':'PASS_HOST_UI_SMOKE','architecture':platform.machine(),
          'library_sha256':hashlib.sha256(library.read_bytes()).hexdigest(),
          'checks':checks,'board_test':'NOT_RUN',
          'limits':'Headless x86 Linux render/API test; not ARM binary or real input/display validation.'}
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result))
