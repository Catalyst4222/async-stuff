import asyncio
import warnings
from asyncio import streams, events, tasks, create_subprocess_exec
from asyncio.subprocess import SubprocessStreamProtocol, Process

_DEFAULT_LIMIT = 2 ** 16  # 64 KiB

asyncio.subprocess


# noinspection PyUnresolvedReferences
class LastingProcess(Process):
    async def _feed_stdin(self, input_):
        debug = self._loop.get_debug()
        self.stdin.write(input_)
        if debug:
            logger.debug(
                '%r communicate: feed stdin (%s bytes)', self, len(input_))
        try:
            await self.stdin.drain()
        except (BrokenPipeError, ConnectionResetError) as exc:
            # communicate() ignores BrokenPipeError and ConnectionResetError
            if debug:
                logger.debug('%r communicate: stdin got %r', self, exc)

        if debug:
            logger.debug('%r communicate: close stdin', self)


    async def _read_stream(self, fd):
        transport = self._transport.get_pipe_transport(fd)
        if fd == 2:
            stream = self.stderr
        else:
            assert fd == 1
            stream = self.stdout
        if self._loop.get_debug():
            name = 'stdout' if fd == 1 else 'stderr'
            logger.debug('%r communicate: read %s', self, name)
        output = await stream.read()
        if self._loop.get_debug():
            name = 'stdout' if fd == 1 else 'stderr'
            logger.debug('%r communicate: close %s', self, name)
        return output

    async def communicate(self, input_=None):
        stdin = self._feed_stdin(input_) if input_ is not None else self._noop()
        stdout = self._read_stream(1) if self.stdout is not None else self._noop()
        stderr = self._read_stream(2) if self.stderr is not None else self._noop()
        stdin, stdout, stderr = await tasks.gather(stdin, stdout, stderr,
                                                   loop=self._loop)
        await self.wait()
        return stdout, stderr


# noinspection PyProtectedMember
async def create_superprocess_exec(program, *args, stdin=-1, stdout=-1,
                                   stderr=-1, loop=None,
                                   limit=_DEFAULT_LIMIT, **kwds):
    if loop is None:
        loop = events.get_event_loop()
    else:
        warnings.warn("The loop argument is deprecated since Python 3.8 "
                      "and scheduled for removal in Python 3.10.",
                      DeprecationWarning,
                      stacklevel=2
                      )

    def protocol_factory():
        return SubprocessStreamProtocol(limit=limit,
                                        loop=loop)

    transport, protocol = await loop.subprocess_exec(
        protocol_factory,
        program, *args,
        stdin=stdin, stdout=stdout,
        stderr=stderr, **kwds)
    return LastingProcess(transport, protocol, loop)


async def main():
    # proc = await create_subprocess_exec('bash', stdin=-1, stdout=-1,
    #                                     stderr=-1)
    # print(f'{proc=}')
    # proc.stdin.write(b'echo "hi"')
    # print('sent')
    # stdout = proc.stdout.readline
    # stderr = proc.stderr.readline
    # futures = await asyncio.gather(stdout(), stderr())
    # print(futures)
    # print('read')
    # await proc.stdin.drain()
    # print('drained')

    proc = await create_superprocess_exec('bash', '-i', stdin=-1, stdout=-1, stderr=-1)
    print('proc')
    print(await proc.communicate(b'ls -l'))
    print('done')

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

