#include <Python.h>

static PyObject *SpamError;

static PyObject *
spam_system(PyObject *self, PyObject *args)
{
    const char *command;
    int sts;

    if (!PyArg_ParseTuple(args, "s", &command))
        return NULL;
    sts = system(command);
    if (sts < 0) {
        return NULL;
    }
    return PyLong_FromLong(sts);
}

static PyMethodDef EngineRunnerMethods[] = {
    {"run", er_run, METH_VARARGS, "Runs all effects in a multithreaded fashion"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initengine_runner(void)
{
    PyObject *m = Py_InitModule("engine_runner", EngineRunnerMethods);
    if (m == NULL)
        return;
}
