#
# Copyright 2016 Andrew Turner
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#

#
# Basic FreeBSD OS awareness handler
#

from osapi import DebugSessionException, Model

from contexts import ContextsProvider
from processes import AllProc

def areOSSymbolsLoaded(debugger):
    ''' Checks if we have loaded symbols.'''
    return debugger.symbolExists("early_boot")

def isOSInitialised(debugger):
    '''Returns true when we are scheduling.'''
    try:
        # TODO: check if we are scheduling, not just running
        result = debugger.evaluateExpression("early_boot")
        return result.readAsNumber() == 0
    except DebugSessionException:
        return False

def getOSContextProvider():
    '''Returns the thread context provider.'''
    return ContextsProvider()

def getDataModel():
    '''Returns the data model object, includes the OS specific table views.'''
    return Model("FreeBSD", [AllProc()])
