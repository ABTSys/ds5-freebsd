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

from osapi import Table
from osapi import createField
from osapi import createNumberCell, createTextCell, createAddressCell
from osapi import DECIMAL, TEXT, ADDRESS

class AllProc(Table):
    def __init__(self):
        id = "allproc"
        fields = [
            createField(id, "pid", DECIMAL),
            createField(id, "tid", DECIMAL),
            createField(id, "comm", TEXT),
            createField(id, "name", TEXT),
            createField(id, "state", TEXT),
            createField(id, "wchan", TEXT),
        ]
        Table.__init__(self, id, fields)

    def getRecords(self, debugger):
        '''Returns the data foe the ps like table.'''

        # The states the thread could be in
        states = [
            "TDS_INACTIVE",
            "TDS_INHIBITED",
            "TDS_CAN_RUN",
            "TDS_RUNQ",
            "TDS_RUNNING"
        ]

        records = []

        # Loop over all processes, and all of their threads
        proc = debugger.evaluateExpression("allproc.lh_first")
        while proc.readAsNumber() != 0:
            proc_members = proc.dereferencePointer().getStructureMembers()
            thread = \
              proc_members["p_threads"].getStructureMembers()["tqh_first"]
            while thread.readAsNumber() != 0:
                thread_members = \
                  thread.dereferencePointer().getStructureMembers()

                # Read the state, this appears to be read as big-endian,
                # possibly because it's an enum.
                state = thread_members["td_state"].readAsNumber()

                # Read the wait message, or an empty string if there is none
                wmesg = ""
                wchan = thread_members["td_wchan"].readAsNumber()
                if wchan != 0:
                    tmp_wmesg = thread_members["td_wmesg"].readAsNumber()
                    if tmp_wmesg != 0:
                        wmesg = thread_members["td_wmesg"].readAsNullTerminatedString()

                # Add the row data
                cells = [
                    createNumberCell(proc_members["p_pid"].readAsNumber()),
                    createNumberCell(thread_members["td_tid"].readAsNumber()),
                    createTextCell(
                      proc_members["p_comm"].readAsNullTerminatedString()),
                    createTextCell(
                      thread_members["td_name"].readAsNullTerminatedString()),
                    createTextCell(states[state >> 24]),
                    createTextCell(wmesg)
                ]
                # And append it to the list of records
                records.append(self.createRecord(cells))

                thread = \
                  thread_members["td_plist"].getStructureMembers()["tqe_next"]

            proc = proc_members["p_list"].getStructureMembers()["le_next"]

        return records
