"""
Generates a report with all-time stats
"""
import os
import webbrowser

import jinja2

import chatstat
import loader
import plotly.offline as po
from pathlib import Path
from plotly.subplots import make_subplots
from tkinter import Tk
from tkinter.filedialog import askdirectory


if __name__ == "__main__":

    msg_dir = chatstat.get_message_dir()

    try:
        print(f"Parsing data from {msg_dir}")
        chat_df, msg_df = loader.parse_from_json(msg_dir)
        loader.persist(msg_df, chat_df)
    except Exception as e:
        print("Could not load messenger data")
        print(f"Exception caught: {e}")
        quit()

    # chat_df, msg_df = loader.load_from_csv()

    cs = chatstat.ChatStat(chat_df, msg_df)

    # who are you chatting with?
    who = make_subplots(rows=2, cols=1, specs=[[{"type": "bar"}], [{"type": "bar"}]],
                        subplot_titles=['Rozložení zpráv mezi studenty', 'Celkový počet zpráv ve skupině'])
    who.add_trace(cs.sent_from(top=35, omit_first=True, kind='bar', show=False), row=1, col=1)
    # who.add_trace(cs.chat_counts(top=35, omit_first=True, show=False), row=2, col=1)
    who.add_trace(cs.biggest_chat(top=1, kind='bar', show=False), row=2, col=1)
    who.update_layout(height=950, width=950, showlegend=False)
    who_html = po.plot(who, output_type='div')


    # who = make_subplots(rows=1, cols=2, specs=[[{"type": "bar"}, {"type": "bar"}]],
    #                     subplot_titles=['# of Messages by Sender', '# of Chats by Sender'])
    # who.add_trace(cs.sent_from(top=10, omit_first=True, kind='bar', show=False), row=1, col=1)
    # who.add_trace(cs.chat_counts(top=10, omit_first=True, show=False), row=1, col=2)
    # # who.add_trace(cs.biggest_chat(top=30, kind='bar', show=False), row=2, col=1)
    # who.update_layout(height=950, width=950, showlegend=False, title_text="Who are you chatting with?")
    # who_html = po.plot(who, output_type='div')

    # proportional
    who_pct = make_subplots(rows=1, cols=1, specs=[[{"type": "pie"}]])
    who_pct.add_trace(cs.sent_from(top=10, omit_first=True, kind='pie', show=False), row=1, col=1)
    # who_pct.add_trace(cs.biggest_chat(top=10, kind='pie', show=False), row=1, col=2)
    who_pct.update_layout(height=475, width=950, showlegend=True)
    proportional_html = po.plot(who_pct, output_type='div')


    # how are you chatting?
    how = make_subplots(rows=1, cols=2, specs=[[{"type": "pie"}, {"type": "pie"}]])
    how.add_trace(cs.msg_types(show=False), row=1, col=1)
    how.add_trace(cs.audio_count_per_sender_pie(show=False), row=1, col=2)
    how.update_layout(height=475, width=950, showlegend=True)
    how_html = po.plot(how, output_type='div', config={'displayModeBar': False})

    # when are you chatting?
    yearly_graph, monthly_graph, hourly_graph, minutely_graph, weekday_graph, daily_graph = cs.time_stats(show=False)
    when = make_subplots(
        rows=3, cols=2, specs=[[{"type": "bar"}] * 2] * 3,
        subplot_titles= ["Ročně", "Měsíčně", "Hodinově", "Minutu po minutě", "Denní maximum 😎", "Den v týdnu"]
    )
    when.add_trace(yearly_graph, row=1, col=1)
    when.add_trace(monthly_graph, row=1, col=2)
    when.add_trace(hourly_graph, row=2, col=1)
    when.add_trace(minutely_graph, row=2, col=2)
    when.add_trace(weekday_graph, row=3, col=2)
    when.add_trace(daily_graph, row=3, col=1)
    when.update_layout(height=950, width=950, showlegend=False) # Kdy si píšem?
    when_html = po.plot(when, output_type='div', config={'displayModeBar': False})

    # what are you saying?
    lengths = [3,5,7, 9]
    three, five, seven, nine = cs.word_counts(top=20, length=lengths, show=False)
    what = make_subplots(
        rows=len(lengths), cols=1, specs=[[{'type': 'bar'}]] * 4,
        subplot_titles=[f"Nejpoužívanější slova s {l} a více písmeny" for l in lengths],
    )
    what.add_trace(three, row=1, col=1)
    what.add_trace(five, row=2, col=1)
    what.add_trace(seven, row=3, col=1)
    what.add_trace(nine, row=4, col=1)
    what.update_layout(height=1200, width=950, showlegend=False, title_text=None) # Co si píšem? A neopkují se nám ty slova? 😏
    what_html = po.plot(what, output_type='div', config={'displayModeBar': False})


    # audion comperison
    # audio = make_subplots(rows=1, cols=1, specs=[[{"type": "bar"}]])
    # audio.add_trace(cs.audio_count_per_month_sender(show=False), row=1, col=1)
    # audio.update_layout(height=475, width=950, showlegend=True, title_text="A co slyšíme?")
    # html += po.plot(audio, output_type='div')


    # jinja template in templates folder
    templateLoader = jinja2.FileSystemLoader(searchpath="./templates")
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = "oneGroup.jinja2"
    template = templateEnv.get_template(TEMPLATE_FILE)

    # render template
    outputText = template.render(
        who_html=who_html,
        proportional_html=proportional_html,
        how_html=how_html,
        when_html=when_html,
        what_html=what_html,
    )

    FILE_NAME = "output.html"
    # save to file
    with open(FILE_NAME, "w") as f:
        f.write(outputText)
        f.close()


    # open in browser
    chatstat.serve_file(FILE_NAME)

    print("Done")