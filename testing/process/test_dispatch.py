from glas_process.procdir import ProcDir
from juggler.model import Task

def test_getid(tmpdir):

    p = ProcDir(None, tmpdir, Task(_id='test'))
    id = p.get_id('python')
    assert id == 'test:python'
    id = p.get_id('python')
    assert id == 'test:python_1'
    id = p.get_id('python', 'python')
    assert id == 'python'
