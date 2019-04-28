import appuifw, e32, wlantools, math, audio, graphics

class PeriodicRefresh:
    """
    This class creates objects that periodically call a function. It uses the "e32.Ao_timer" function.
    """
    def __init__(self, period, callback):
        """
        Initialization of the "PeriodicRefresh" instance. the "period" argument is the desired perido in seconds and the "callback" argument is the function to call.
        """
        # We register the arguments.
        self._period = period
        self._callback = callback
        # We create a "e32.Ao_timer" instance.
        self._timer = e32.Ao_timer()
        # We start the perdiodic calls.
        self.refresh()

    def refresh(self):
        """
        This method is called periodically and calls the desired function.
        """
        # We call the desired function.
        self._callback()
        # We wait for the period and then call this method.
        self._timer.after(self._period, self.refresh)


class NetworkStats:
    """
    This class represents the statistics about the WLAN networks. It has a single attribute, "networks", a dictionary associating to WLAN network names a frequency and a signal level. The frequency represents wether a network is constantly in range. The signal level is the reception level in dbm and is "None" if the network is out of range.
    """

    def __init__(self):
        """
        Initialization of the "NetworkStats" instance.
        """
        # We initialize the "networks" attribute with an empty dictionary.
        self.networks = {}

    def check_networks(self):
        """
        This method returns a dictionary: for each WLAN network in range it associates to the name the signal level. It uses the "wlantools.scan" function.
        """
        return dict(zip([network["SSID"] for network in wlantools.scan()], [network["RxLevel"] for network in wlantools.scan()]))

    def refresh(self):
        """
        This method updates the "networks" argument. For each new network, an audio announcement is made, its frequency is set to 1 and its signal level is registered. For each existing network, if it is in range, its frequency is incremented by 1 and its signal level is updated; if it is out of range, its frequency is decremented by 1 and its signal level is set to "None". Networks with a frequency equal to 0 are removed.
        """
        # We check for the current networks in range.
        visible_networks_levels = self.check_networks()
        # For each network present in the "networks" attribute:
        for network in self.networks.keys():
            # if it is not visible,
            if not network in visible_networks_levels.keys():
                # its frequency is decremented by 1 and its signal level is set to None,
                self.networks[network]["rate"] -= 1
                self.networks[network]["level"] = None
                # and if its frequency is now equal to 0, the audio announcement is made and the network is removed from the "networks" attribute.
                if self.networks[network]["rate"] == 0:
                    audio.say(u"%s out of range" % network)
                    del self.networks[network]
        # For each visible network:
        for network in visible_networks_levels.keys():
            # if the network is not yet in the "networks" attribute, the audio announcement is made, and it is added to the "networks" attribute with the frequency 0 and an arbitrary signal level (i.e. "None");
            if not network in self.networks.keys():
                audio.say(u"%s now in range" % network)
                self.networks[network] = {"rate" : 0, "level" : None}
            # in any case, the frequency associated to the network is incremented by 1 and its signal level is updated.
            self.networks[network]["rate"] += 1
            self.networks[network]["level"] = visible_networks_levels[network]
            
    def __call__(self):
        """
        This method returns a dictionary containing, for each network name, its rate defined as "tanh(f / 10)" where "f" is its frequency and its signal level.
        """
        # For each frequency, we apply the function x -> tanh(x / 10).
        stats = {}
        for network in self.networks.keys():
            stats[network] = {"rate" : math.tanh(self.networks[network]["rate"] / 10.), "level" : self.networks[network]["level"]}
        return stats


def word_dimension(word, font):
    """
    This function takes for arguments a word, a font (as defined in the "appuifw" module) and returns the size in pixels of the smallest rectangle surrounding the word "word" written with the font "font".
    """
    # "display" is a "appuifw.Canvas" instance associated to the global "appuifw.app.body". The "measure_text" method first return value contains the coordinates of the smallest rectangle surrounding the text given as the first argument (here word) with the font given as the second argument.
    measure = display.measure_text(word, font)
    # We return the width and height of the surrounding rectangle.
    return (measure[0][2] - measure[0][0] + 1, measure[0][3] - measure[0][1] + 1)


def font_height(font):
    """
    This function takes for argument a font (as defined in the "appuifw" module) and returns its height : the height in pixels of a capital letter written with that font.
    """
    # We return the vertical dimension of the word "A" in the font "font".
    return word_dimension(u"A", font)[1]


def get_font(face, height, style = None):
    """
    This function takes for arguments the name of a font "face" (as defined in the "appuifw" module), a height in pixels "height" and optionaly a font style. It returns a similar font wich size is the highest possible provided its height is smaller or equal to "height". It uses dichotomy for better performances.
    """
    # "max_size" is the maximum value for a font size.
    max_size = 300
    # "size" is the font size the algorithm will compute. Its initial candidate value is arbitrary (here 0).
    size = 0
    # "floor" is the lowest possible value for "size". Its initial value is 0.
    floor = 0
    # "ceil" is the highest possible value for "size". Its initial value is "max_size".
    ceil = max_size
    # Main loop
    while True :
        # If the height corresponding to the current size candidate is higher than "height":
        if (font_height((face, size, style)) > height):
            # the new highest possible value is the current size,
            ceil = size
            # the new candidate value for "size" is in the middle between the current size and the lowest possible value "floor".
            size = (floor + size) / 2
        # If the height corresponding to the current size candidate is smaller than "height" or equal:
        else:
            # the new lowest possible value is the current size,
            floor = size
            # the new candidate value for "size" is in the middle between the current size and the highest possible value "ceil".
            # However, if this new candidate is equal to the current size, the algorithm has converged and we break the main loop.
            if (size != (size + ceil) / 2):
                size = (size + ceil) / 2
            else:
                break
    # The function returns the font with the computed size.
    return (face, size, style)


def get_signal_color(signal):
    """
    This function returns a color (as defined in the "appuifw" module) corresponding to as signal level (in dbm). If the signal is "None" it returns light silver. Otherwise it returns green which is lighter if the signal level is higer.
    """
    if signal == None:
        return (160, 160, 160)
    else:
        return (0, max(255 + signal, 100), 0)


def display_networks():
    """
    This function draws the network names. To avoid the display to blink, we first generate a "graphics.Image" object containing the content of the display and then display it.
    """
    # We create a new content which size is half the screen.
    content = graphics.Image.new((display.size[0], display.size[1] / 2))
    # We define "H", the maximum height used by the list of networks.
    H = content.size[1]
    # We define "h_min", the minimum height of a name.
    h_min = 0.1 * H
    # We define "h_max", the maximum height of a name.
    h_max = 0.5 * H
    # The global varialbe "stats", instance of the "NetworkStats" returns a dictionary containing, for each network name, its rate when it is called as a function.
    current_stats = networks_stats()
    # "h" is a list containing the heights of the network names: the height is proportional to the rate except that the floor height is imposed.
    h = map(lambda name: max(h_max * current_stats[name]["rate"], h_min), current_stats.keys())
    # If the names wouldn't fit with the current heights, we downscale all the heights so that the names fit.
    if sum(h) > H:
        h = map(lambda height: height * H / sum(h), h)
    # The integer "y_offset" initial value is set so the names will be vertically centered.
    y_offset = (H - sum(h)) / 2
    # "h" is redefined as a dictionary associating to each network name its height.
    h = dict(zip(current_stats.keys(), h))
    # We loop over the network names.
    for name in current_stats.keys():
        # Font is the font with which will be written the current name.
        font = get_font(u"normal", h[name])
        # The integer "y_offset" is the vertical position of the bottom of the current name: it is the sum of the heights of the previously drawn names and of the current name plus its initial value.
        y_offset += h[name]
        # The integer "x_offset" is the horizontal position of the left of the current name. We set it so the name is centered if it is not larger than the screen.
        x_offset = max((display.size[0] - word_dimension(name, font)[0]) / 2, 0)
        # We draw the name with the correct color and the correct font.
        content.text((x_offset, y_offset), name, get_signal_color(current_stats[name]["level"]), font)
    # We add the new content as the top half of the screen.
    display.blit(content, target = (0, 0))


def refresh_networks():
    """
    This function refreshes the display of the network names.
    """
    # We update the network statistics.
    networks_stats.refresh()
    # We refresh the networks display.
    display_networks()


def display_sensors():
    """
    This function draws the sensors. To avoid the display to blink, we first generate a "graphics.Image" object containing the content of the display and then display it.
    """
    # We create a new content which size is half the screen.
    content = graphics.Image.new((display.size[0], display.size[1] / 2))
    # Todo
    content.text((0, content.size[1] / 2), u"Sample sensors display")
    # We add the new content as the bottom half of the screen.
    display.blit(content, target = (0, display.size[1] / 2))


def refresh_sensors():
    """
    This function refreshes the display of the sensors data.
    """
    # We refresh the sensors display.
    display_sensors()


def redraw_display(canvas_box = None):
    """
    This function is the redraw callback handler of the "display" "appuifwCanvas" instance and thus takes as argument coordinates of the region to redraw. However, the entire region is always redrawn.
    """
    # During the redrawing process we display "Loading..." on the screen.
    display.text((0, display.size[1] / 2), u"Loading...")
    # We refresh the networks data.
    refresh_networks()
    # We refresh the sensors data.
    refresh_sensors()


def quit():
    """
    Application exit key handler.
    """
    # "app_lock" is the main "e32.Ao_lock" instance.
    app_lock.signal()


## MAIN PROGRAM

# We define the application exit key handler.
appuifw.app.exit_key_handler = quit

# We set the screen to "full" mode
appuifw.app.screen = "full"

# We define the refresh interval
networks_time_interval = 15;
sensors_time_interval = 15;

# We create the global varialbe "networks_stats", instance of the "NetworkStats" class to contain statistics about the WLAN networks.
networks_stats = NetworkStats()

# We create "display", the "appuifw.Canvas" instance, as the application display.
display = appuifw.Canvas(redraw_callback = redraw_display)
appuifw.app.body = display

# Every "networks_time_interval" seconds, we refresh the display of the network names.
networks_refresh = PeriodicRefresh(networks_time_interval, refresh_networks)

# Every "sensors_time_interval" seconds, we refresh the display of the sensors data.
sensors_refresh = PeriodicRefresh(sensors_time_interval, refresh_sensors)

# We keep the backlight on by maintaining an activity every 5 seconds.
light_refresh = PeriodicRefresh(5, e32.reset_inactivity)

# We wait until the user exits.
app_lock = e32.Ao_lock()
app_lock.wait()

