# Blinds Control for Home Assistant

A Home Assistant integration for controlling motorized blinds using Raspberry Pi GPIO and servo motors.

## Features

- **Native Home Assistant Integration**: Blinds appear as cover entities in Home Assistant
- **Position Control**: Set blinds to any percentage (0-100%)
- **Voice Control**: Works with Google Assistant, Amazon Alexa, and other voice assistants
- **Automation Support**: Use in automations, scripts, and scenes
- **Real-time Updates**: Position updates automatically
- **Web Interface**: Advanced configuration through web interface

## Requirements

- Raspberry Pi with Home Assistant installed
- Motorized blinds with servo motors
- pigpio library installed
- Existing Blinds Control service running on port 80

## Installation

### Option 1: HACS (Recommended)

1. Install [HACS](https://hacs.xyz/) if you haven't already
2. Add this repository to HACS:
   - Go to HACS > Integrations
   - Click the "+" button
   - Add repository: `yourusername/blinds_integration`
   - Select "Integration" category
3. Search for "Blinds Control" in the integrations list
4. Click "Download"
5. Restart Home Assistant

### Option 2: Manual Installation

1. Copy the `custom_components/blinds_control` folder to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** > **Devices & Services**
2. Click **"+ Add Integration"**
3. Search for **"Blinds Control"**
4. Enter the host and port of your Blinds Control service:
   - **Host**: `localhost` (or your Pi's IP address)
   - **Port**: `80` (default)
5. Click **"Submit"**

## Usage

Once configured, you'll have cover entities for each blind:

- **cover.living_room_left**
- **cover.living_room_right**
- **cover.dining_room_left**
- **cover.dining_room_right**
- **cover.kitchen_window**
- **cover.kitchen_door_left**
- **cover.kitchen_door_right**
- **cover.master_bedroom_left**
- **cover.master_bedroom_right**
- **cover.guest_bedroom_left**
- **cover.guest_bedroom_right**
- **cover.office_left**
- **cover.office_right**
- **cover.kitchen_door**

### Voice Commands

- "Hey Google, open the living room blinds"
- "Hey Google, close the kitchen blinds"
- "Hey Google, set the dining room blinds to 50%"

### Automations

```yaml
# Close all blinds at sunset
automation:
  - alias: "Close Blinds at Sunset"
    trigger:
      platform: sun
      event: sunset
    action:
      - service: cover.close_cover
        target:
          entity_id:
            - cover.living_room_left
            - cover.living_room_right
            - cover.dining_room_left
            - cover.dining_room_right
```

### Scripts

```yaml
# Morning routine
script:
  morning_routine:
    sequence:
      - service: cover.set_cover_position
        target:
          entity_id: cover.living_room_left
        data:
          position: 25
      - service: cover.set_cover_position
        target:
          entity_id: cover.kitchen_window
        data:
          position: 50
```

## Web Interface

For advanced configuration (setting open/close positions, testing servos), use the web interface:

1. Navigate to `http://your-pi-ip/config` in your browser
2. Configure open and close positions for each blind
3. Test servo movements
4. Download/upload configuration files

## Troubleshooting

### Integration Not Found
- Make sure the `custom_components/blinds_control` folder is in your Home Assistant config directory
- Restart Home Assistant after installation

### Connection Errors
- Verify your Blinds Control service is running on port 80
- Check that the host and port are correct in the integration configuration
- Ensure Home Assistant can reach the service (try `http://localhost:80/status` in a browser)

### Blinds Not Responding
- Check the Home Assistant logs for error messages
- Verify your `blindsconfig.json` file is properly configured
- Test the web interface to ensure the service is working

## Support

For issues and questions:
1. Check the Home Assistant logs
2. Test the web interface directly
3. Verify your Blinds Control service is running properly

## License

This project is licensed under the MIT License. 