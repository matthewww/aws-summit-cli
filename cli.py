import questionary

from events import fetch_events
from aws_agenda import fetch_sessions, UNDISCOVERABLE


def on_progress(status):
    print(f"\r{' ' * 60}\r{status}", end="", flush=True)


def main():
    events = fetch_events(on_progress=on_progress)
    print("\r" + " " * 60 + "\r", end="")
    labels = [f"{e['location']} — {e['date']}" for e in events]

    while True:
        choice = questionary.select("Pick an AWS Summit:", choices=labels).ask()
        if choice is None:
            return

        event = events[labels.index(choice)]

        on_progress(f"Fetching sessions for {event['title']}...")
        result = fetch_sessions(event, on_progress=on_progress)
        print("\r" + " " * 60 + "\r", end="")

        if result == UNDISCOVERABLE:
            print(f"Couldn't find this event's session data — AWS renders it fully "
                  f"client-side for this one. Check manually: {event['agenda_url']}\n")
            continue
        if result is None:
            print("No agenda data available for this event yet.\n")
            continue

        total_hits, out_path = result
        print(f"Fetched {total_hits} sessions -> {out_path}\n")


if __name__ == "__main__":
    main()
