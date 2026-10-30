/** @file */
#include "flight_controller.h"

// Example function to demonstrate the use of MC/DC (code coverage metric).
// See this youtube video for more information:
// https://www.youtube.com/watch?v=k0_PF8MtEEo

/**
 * @trace Abort decision logic
 * type: impl
 * id: SWIMPL_FC-001
 * implements: SWDD_FC-100, SWDD_FC-101, SWDD_FC-102
 */
boolean CheckAbort(boolean off_course, boolean abort_commanded, boolean valid_abort_command)
{
    if (off_course || (abort_commanded && valid_abort_command))
    {
        return TRUE;
    }
    else
    {
        return FALSE;
    }
}

/**
 * @trace Flight Controller's main runnable
 * type: impl
 * id: SWIMPL_FC-002
 * implements: SWDD_FC-103, SWDD_FC-200, SWDD_FC-201, SWDD_FC-202, SWDD_FC-203, SWDD_FC-204
 */
void flightController(void)
{
    boolean off_course;
    RteGetOffCourse(&off_course);
    boolean abort_commanded = RteGetAbortCommanded();
    boolean valid_abort_command = RteGetValidAbortCommand();

    boolean abort = CheckAbort(off_course, abort_commanded, valid_abort_command);
    RteSetSelfDestructState(abort);
}
