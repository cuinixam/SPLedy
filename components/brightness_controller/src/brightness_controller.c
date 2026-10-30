/**
 * @file brightness_controller.c
 * @brief Module to control the brightness.
 *
 * @docs
 * The brightness controller sets the brightness of the LED. Its runnable
 * computes a brightness value from 0 to 255 in every task cycle and writes it
 * to the RTE.
 *
 * The Kconfig choice `BRIGHTNESS_ADJUSTMENT` selects the mode:
 *
 * - `BRIGHTNESS_ADJUSTMENT_AUTOMATIC`: the brightness ramps up and down by itself.
 * - `BRIGHTNESS_ADJUSTMENT_MANUAL`: the brightness follows the main control knob.
 * @enddocs
 */

#include "brightness_controller.h"
#include "rte.h"

#ifdef CONFIG_BRIGHTNESS_ADJUSTMENT_AUTOMATIC

/**
 * @docs
 * In automatic mode the brightness ramps linearly from a minimum up to a
 * maximum and back down. `BRIGHTNESS_ADJUSTMENT_PERIOD` sets the length of one
 * full cycle in seconds. The controller converts it to task cycles and also
 * writes the current cycle position to the RTE.
 * @enddocs
 */
#define BRIGHTNESS_PERIOD_TICKS ((unsigned int)((CONFIG_BRIGHTNESS_ADJUSTMENT_PERIOD * 1000) / BRIGHTNESS_TASK_PERIOD))

/**
 * @docs
 * Returns the brightness for the current position in the cycle and moves the
 * position one task cycle ahead. The first half of the cycle ramps up, the
 * second half ramps down.

 * @trace Periodic Brightness Adjustment
 * type: impl
 * id: SWIMPL_BC-001
 * implements: SWDD_BC-100, SWDD_BC-102
 * @enddocs
 */
SPLE_TESTABLE_STATIC brightness_t periodicBrightnessAdjustment(BrightnessAdjustmentData *data)
{
    brightness_t brightnessValue = 0;

    if (data->ticksCounter < data->halfPeriod)
    {
        // Ramp up linearly from min to max
        brightnessValue = data->minBrightness + ((data->maxBrightness - data->minBrightness) * data->ticksCounter) / data->halfPeriod;
    }
    else
    {
        // Ramp down linearly from max to min
        brightnessValue = data->maxBrightness - ((data->maxBrightness - data->minBrightness) * (data->ticksCounter - data->halfPeriod)) / data->halfPeriod;
    }

    // Increment and reset ticksCounter based on the period
    data->ticksCounter = (data->ticksCounter + 1) % data->period;

    return brightnessValue;
}

#else /* CONFIG_BRIGHTNESS_ADJUSTMENT_AUTOMATIC */

/**
 * @docs
 * In manual mode the brightness follows the main control knob. The knob value
 * in percent (0 to 100) is scaled to the brightness range (0 to 255).
 * @enddocs
 * @trace Manual Brightness Adjustment
 * type: impl
 * id: SWIMPL_BC-002
 * implements: SWDD_BC-100, SWDD_BC-101, SWDD_BC-201
 */
static brightness_t manualBrightnessAdjustment(void)
{
    percentage_t mainKnobValue = RteGetMainKnobValue();
    brightness_t brightnessValue = 0;

    if (mainKnobValue == 0)
    {
        brightnessValue = 0;
    }
    else
    {
        brightnessValue = (mainKnobValue * 255) / 100;
    }
    return brightnessValue;
}

#endif /* CONFIG_BRIGHTNESS_ADJUSTMENT_AUTOMATIC */

/**
 * @docs
 * Runnable of the component. Computes the brightness in the selected mode and
 * writes it to the RTE.
 * @enddocs
 * @trace Brightness Controller runnable
 * type: impl
 * id: SWIMPL_BC-003
 * implements: SWDD_BC-200, SWDD_BC-202, SWDD_BC-203
 */
void brightnessController(void)
{
    brightness_t brightnessValue = 0;
#ifdef CONFIG_BRIGHTNESS_ADJUSTMENT_AUTOMATIC
    static BrightnessAdjustmentData data = {
        .ticksCounter = 0,
        .period = BRIGHTNESS_PERIOD_TICKS,
        .halfPeriod = BRIGHTNESS_PERIOD_TICKS / 2,
        .maxBrightness = 200,
        .minBrightness = 50};

    brightnessValue = periodicBrightnessAdjustment(&data);
    RteSetBrightnessAdjustmentCounter(data.ticksCounter);
#elif defined(CONFIG_BRIGHTNESS_ADJUSTMENT_MANUAL)
    brightnessValue = manualBrightnessAdjustment();
#endif
    RteSetBrightnessValue(brightnessValue);
}
