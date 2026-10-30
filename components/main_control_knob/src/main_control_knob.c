/**
 * @file
 * @brief Implementation of the main control knob module
 */

#include "main_control_knob.h"
#include "rte.h"

#define CONTROL_KEY_UP KEY_UP
#define CONTROL_KEY_DOWN KEY_DOWN
#define KNOB_UPDATE_INCREMENT 2u

/**
 * @trace Main Control Knob's main function
 * type: impl
 * id: SWIMPL_MCK-001
 * implements: SWDD_MCK-100, SWDD_MCK-101, SWDD_MCK-200, SWDD_MCK-201, SWDD_MCK-202, SWDD_MCK-203
 */
void mainControlKnob(void)
{
    percentage_t currentValue = RteGetMainKnobValue();
    if (RteIsKeyPressed(CONTROL_KEY_UP))
    {
        // Increase knob's percentage value by 5 with a maximum of 100.
        if (currentValue < (100 - KNOB_UPDATE_INCREMENT))
        {
            currentValue += KNOB_UPDATE_INCREMENT;
        }
        else
        {
            currentValue = 100;
        }
    }
    else if (RteIsKeyPressed(CONTROL_KEY_DOWN))
    {
        // Decrease knob's percentage value by 5 with a minimum of 0.
        if (currentValue > KNOB_UPDATE_INCREMENT)
        {
            currentValue -= KNOB_UPDATE_INCREMENT;
        }
        else
        {
            currentValue = 0;
        }
    }
    RteSetMainKnobValue(currentValue);
}
