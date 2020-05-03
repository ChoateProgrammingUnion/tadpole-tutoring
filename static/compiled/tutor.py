from browser import document, alert
alert("test")

def echo(ev):
    alert(document["#switch-tutor"].value)
document["#switch-tutor"].bind("click", echo)
