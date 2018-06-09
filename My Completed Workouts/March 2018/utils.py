from ipywidgets import DOMWidget, Layout, Button
from IPython.display import display, Javascript
from traitlets import Unicode, validate
import time
import threading



class Timer(DOMWidget):
    _view_name = Unicode('TimerView').tag(sync=True)
    _view_module = Unicode('Timer').tag(sync=True)
    _view_module_version = Unicode('0.2.0').tag(sync=True)
    value = Unicode('00:00:00').tag(sync=True)


    times_pressed = 0
    go_time = False
    event = threading.Event()
    times_up = False

    # this method starts and stops the timer based on how many times the user clicked it
    def threaded_timer(self,b,max_time=180):
        if self.times_up:
            b.disabled = True
            
        if self.times_pressed == 0:
            self.times_pressed += 1
            b.description = "PAUSE"
            b.button_style = "warning"
            b.disabled = True
            self.go_time = True
            thread = threading.Thread(target=self.timeit, args=(b,max_time))
            thread.start()
            time.sleep(1) # prevents user from spamming start/stop buttom which would throw off the time
            b.disabled = False

        # PAUSE button pushed
        elif (self.times_pressed % 2) != 0:
            self.times_pressed += 1
            b.description = "RESUME"
            b.button_style= "success"
            b.disabled = False
            self.event.clear()
            self.go_time = False

        # RESUME button pushed
        elif (self.times_pressed % 2) == 0:
            self.times_pressed += 1
            self.go_time = True
            b.description="PAUSE"
            b.button_style="warning"
            b.disabled = True
            self.event.set()
            time.sleep(1) # prevents user from spamming start/stop buttom which would throw off the time
            b.disabled = False

    # this is what's actually keeping track of the time and updating the custom Timer widget
    def timeit(self, b, max_time=180):
        hours = 0
        mins = 0
        secs = 0
        for i in range(1,(max_time*60+1)):
            if self.go_time:
                if (i % 60) == 0:
                    if (i % 3600) == 0:
                        secs = 0
                        mins = 0
                        hours += 1
                        if hours == 1:
                            self.two_hour_warning()
                        elif hours == 2:
                            self.one_hour_warning()
                    else:
                        secs = 0
                        mins += 1
                else:
                    secs += 1
                self.value = '{hour:02}:{minute:02}:{second:02}'.format(hour=hours,minute=mins,second=secs)
                time.sleep(1)

            else:
                self.event.wait()
        else:
            b.button_style="danger"
            b.description="TIME'S UP!"
            self.timeup()
            self.times_up = True

    # show user a pop-up notification when they run out of time
    def timeup(self):
        display(Javascript("""
        require(
        ["base/js/dialog"],
        function(dialog) {
            dialog.modal({
                title: "TIME'S UP!",
                body: "CONGRATS! You just finished the workout.  \
                        How'd you feel about your performance? You can continue this workout \
                        if you're feeling particularly inspired today, \
                        but don't fret about trying to get the best/perfect answers. I recommend you just take a few minutes to \
                        reflect on the challenges you overcame and bring \
                        the new you to another workout when you're ready.",
                buttons: {
                    'OK': {}
                         }
                  });

              }
        );
        """))

    # pop-up notification for two hour remaining
    def two_hour_warning(self):
        display(Javascript("""
        require(
        ["base/js/dialog"],
        function(dialog) {
            dialog.modal({
                title: "2 HOURS LEFT",
                body: "Hey there! Just a friendly reminder that you have two more hours.  \
                        Keep up the good work!",
                buttons: {
                    'OK': {}
                         }
                  });

              }
        );
        """))

    # pop-up notification for one hour remaining
    def one_hour_warning(self):
        display(Javascript("""
        require(
        ["base/js/dialog"],
        function(dialog) {
            dialog.modal({
                title: "1 HOUR LEFT",
                body: "Just 1  hour remaining. How's it going? Any exciting results? \
                        Remember not to focus too much time on any one thing. \
                        Consider wrapping up your main section in the next 30-45 mins to give you time \
                        for the conclusion/results section.",
                buttons: {
                    'OK': {}
                         }
                  });

              }
        );
        """))
    
# need this to run to be able to show the timer widget in the front-end    

display(Javascript("""

require.undef('Timer');

define('Timer', ["@jupyter-widgets/base"], function(widgets) {

    var TimerView = widgets.DOMWidgetView.extend({

        render: function() {
            this.value_changed();
            this.model.on('change:value', this.value_changed, this);
        },

        value_changed: function() {
            this.el.textContent = this.model.get('value');
        },
    });

    return {
        TimerView : TimerView
    };
});
"""))

# once a Timer widget is instantiated, this function should be called to display the Timer
def show(timer):
    button = Button(description="START", layout=Layout(width="20%", height='50px'), button_style="success")
    button.style.font_weight = "1000"
    display(button)
    display(timer)
    button.on_click(timer.threaded_timer)
