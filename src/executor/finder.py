from executor.me.sherlock import Sherlock
from executor.me.socialscan import AsyncSocialscan
from executor.executable import IExecutable, IAsyncExecutable


FIND: dict[str, type[IExecutable | IAsyncExecutable]] = {
    'sherlock': Sherlock,
    'socialscan': AsyncSocialscan,
}