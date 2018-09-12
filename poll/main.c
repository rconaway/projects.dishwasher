#include <stdbool.h>
#include <stdint.h>
#include "boards.h"
#include "nordic_common.h"
#include "nrf_error.h"
#include "nrf_drv_timer.h"
#include "app_error.h"

#include "nrf_log.h"
#include "nrf_log_ctrl.h"
#include "nrf_log_default_backends.h"

#define TILT_SWITCH              8

void init()
{
    nrf_gpio_cfg_sense_input(TILT_SWITCH, NRF_GPIO_PIN_PULLDOWN, NRF_GPIO_PIN_SENSE_HIGH);
    
    APP_ERROR_CHECK(NRF_LOG_INIT(NULL));
    NRF_LOG_DEFAULT_BACKENDS_INIT();

    uint32_t time_ms = 1000;
    uint32_t err_code = NRF_SUCCESS;

    nrf_drv_timer_config_t timer_cfg = NRF_DRV_TIMER_DEFAULT_CONFIG;
    err_code = nrf_drv_timer_init(0, &timer_cfg, timer_led_event_handler); 
    APP_ERROR_CHECK(err_code);

    nrf_drv_timer_enable(0);

    NRF_LOG_INFO("Poll example started.");
}

void timer_event_handler(nrf_timer_event_t event_type, void* p_context) 
{
    NRF_LOG_INFO("tick");
}

int main(void)
{
    init();

    uint32_t last = 0;

    while (true)
    {
        NRF_LOG_FLUSH();
	
	uint32_t switch0 = nrf_gpio_pin_read(TILT_SWITCH);
	if (switch0) {
	  if (!last) {
		  NRF_LOG_INFO("switch now ON");
	  }
	} else {
		if (last) {
			NRF_LOG_INFO("switch now OFF");
		}
	}
	last = switch0;
    }
}
