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

from osapi import ExecutionContext
from osapi import ExecutionContextsProvider

import sys

class ContextsProvider(ExecutionContextsProvider):
    def getCurrentOSContext(self, debugger):
        '''Read the context for teh current thread.'''
        curthread = debugger.evaluateExpression("*(((struct pcpu *)$AARCH64::$System::$Thread::$TPIDR_EL1)->pc_curthread)")
        return self.createContext(debugger, curthread)

    def getAllOSContexts(self, debugger):
        '''Read the context for all for all threads.'''
        contexts = []

        # Find the first process in the allproc linked list
        proc = debugger.evaluateExpression("allproc.lh_first")
        while proc.readAsNumber() != 0:
            proc_members = proc.dereferencePointer().getStructureMembers()
            # Get the first thread in the processes thread linked list
            thread = \
              proc_members["p_threads"].getStructureMembers()["tqh_first"]
            while thread.readAsNumber() != 0:
                thread_members = \
                  thread.dereferencePointer().getStructureMembers()
                # Create the context and append it to the list of threads
                contexts.append(
                  self.createContext(debugger, thread.dereferencePointer()))
                # Get the next thread in the list
                thread = \
                  thread_members["td_plist"].getStructureMembers()["tqe_next"]

            # Get the next process in the list
            proc = proc_members["p_list"].getStructureMembers()["le_next"]

        return contexts

    def getOSContextSavedRegister(self, debugger, context, name):
        '''Pull out the registers as they were saved in cpu_switch.'''
        # TODO: Use the frame pointer to pull out the link register value,
        # it should be at the address FP + 8. (FP = x29)
        pcb = context.getAdditionalData()["pcb"].getStructureMembers()
        if name == "PC":
            return pcb["pcb_x"].getArrayElements()[30]
        if name == "SP":
            return pcb["pcb_sp"]
        if name == "FP":
            # TODO: Use fp to get this
            return None
        if name[0] == "X" or name[0] == "W":
            reg = int(name[1:])
            return pcb["pcb_x"].getArrayElements()[reg]
        return None

    def createContext(self, debugger, task):
        '''Create a object from the thread data.'''

        members = task.getStructureMembers()
        # Use the thread id for the ID
        id = members["td_tid"].readAsNumber()
        # And the thread name for the name
        name = members["td_name"].readAsNullTerminatedString()
        # Create the context
        context = ExecutionContext(id, name, None);

        # Add a pointer to the pcb to pull out the registers later
        context.getAdditionalData()["pcb"] = \
          members["td_pcb"].dereferencePointer()

        return context
