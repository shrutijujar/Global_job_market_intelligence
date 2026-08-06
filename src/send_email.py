import yagmail

def send_job_alert(
    recipient,
    title,
    company,
    country,
    url
):

    yag = yagmail.SMTP(
        "shrutijujar321@gmail.com",
        "ixlo vner ezan toir"
    )

    body = f"""
New Job Found!

Title: {title}

Company: {company}

Country: {country}

Apply:
{url}
"""

    yag.send(
        to=recipient,
        subject="New Job Alert",
        contents=body
    )