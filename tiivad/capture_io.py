import sys, types

class OutOfInputsError(RuntimeError):
    pass


class _ListenerStream:
    def __init__(self, data_listener):
        self._data_listener = data_listener


class _InputListenerStream(_ListenerStream):

    def __init__(self, data_listener, inputs_iterator):
        _ListenerStream.__init__(self, data_listener)
        self._inputs_iterator = inputs_iterator

    def fetch_remaining_inputs(self):
        result = []
        while True:
            try:
                result.append(next(self._inputs_iterator))
            except StopIteration:
                break

        return result

    def read(self, limit=-1):
        raise NotImplementedError("The method 'read' on stdin is not supported in testable programs")

    def readline(self, limit=-1):
        if limit > 0:
            raise NotImplementedError("Positive limit/size for method 'readline' on stdin "
                                      "is not supported in testable programs")

        try:
            data = str(next(self._inputs_iterator)) + "\n"
            self._data_listener(data)
            return data
        except StopIteration:
            raise OutOfInputsError("The program asked for more inputs than were available")

    def readlines(self, limit=-1):
        raise NotImplementedError("The method 'readlines' on stdin is not supported in testable programs")


class _OutputListenerStream(_ListenerStream):
    def __init__(self, data_listener):
        _ListenerStream.__init__(self, data_listener)

    def write(self, data):
        self._data_listener(data)

    def writelines(self, lines):
        self._data_listener(lines)


class IOCapturing:
    def __init__(self, inputs=[]):
        self._inputs = inputs

    def __enter__(self):
        self._inputs_iterator = self._create_inputs_iterator(self._inputs)
        self._stream_events = []
        self._original_streams = {}
        self._remaining_inputs = []

        # Remember original streams
        for stream_name in {"stdin", "stdout", "stderr"}:
            self._original_streams[stream_name] = getattr(sys, stream_name)

        # Install fake streams
        sys.stdin = _InputListenerStream(self._record_stdin_data, self._inputs_iterator)
        sys.stdout = _OutputListenerStream(self._record_stdout_data)
        sys.stderr = _OutputListenerStream(self._record_stderr_data)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._remaining_inputs = sys.stdin.fetch_remaining_inputs()

        # restore original streams
        for stream_name in {"stdin", "stdout", "stderr"}:
            setattr(sys, stream_name, self._original_streams[stream_name])

    def _create_inputs_iterator(self, inputs):
        if isinstance(inputs, str):
            return iter(inputs.splitlines())

        try:
            return iter(inputs)
        except TypeError:
            try:
                result = inputs(self)
                assert isinstance(result, types.GeneratorType)
                return result
            except BaseException as e:
                e.message = "Could not create iterator for inputs.\n" + e.message
                raise

    def _record_stdin_data(self, data):
        self._stream_events.append(("stdin", data))

    def _record_stdout_data(self, data):
        self._stream_events.append(("stdout", data))

    def _record_stderr_data(self, data):
        self._stream_events.append(("stderr", data))

    def get_remaining_inputs(self):
        return self._remaining_inputs

    def _get_stream_data(self, stream_names, only_since_last_input):
        result = ""
        i = len(self._stream_events) - 1
        while i >= 0:
            event_stream_name, event_data = self._stream_events[i]

            if only_since_last_input and event_stream_name == "stdin":
                break

            if event_stream_name in stream_names:
                result = event_data + result

            i -= 1

        return result

    def get_io(self):
        return self._get_stream_data({"stdout", "stderr", "stdin"}, False)

    def get_stdout(self):
        return self._get_stream_data({"stdout"}, False)

    def get_last_stdout(self):
        return self._get_stream_data({"stdout"}, True)

    def get_stderr(self):
        return self._get_stream_data({"stderr"}, False)

    def debug(self, *args, sep=' ', end='\n', stream_name="stdout", flush=False):
        """Meant for printing debug information from input generator."""
        print(*args, sep=sep, end=end,
              file=self._original_streams[stream_name], flush=flush)

