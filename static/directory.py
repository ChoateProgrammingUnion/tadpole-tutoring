from browser import document, alert, aio
import javascript
from config import URL

teacher_bio_template = """<aside>
    <center>
        <img alt="Profile Picture" src="https://github.com/identicons/jasonlong.png" height="150">
        <h3>{first_name} {last_name}</h3>
    </center>
    <p><b>Studies at: </b>Choate Rosemary Hall</p>
    <p><b>Subjects Teaching: </b>{subjects}</p>
    <p><b>Email: </b><span>{email}</span></p>
    <p>{bio}</p>
    <a><strong class="tutor-link" id="{id}">Schedule Now</strong></a>
</aside>
"""

def render_tutor_bios(vars):
    """
    Fetches and renders template
    """
    html = ""
    for count, each_var in enumerate(vars):
        # each_var["id"] = str(count)
        each_var['subjects'] = each_var['subjects'].replace("|", ", ")
        html += teacher_bio_template.format(**each_var)

    return len(vars), html

async def search_by_tutor():
    response_dict = await fetch_teachers()
    total_count, tutor_bio_html = render_tutor_bios(response_dict)

    document['schedule-results'].html = tutor_bio_html

    for d in document.select(".tutor-link"):
        d.bind("click", display_tutor_times)