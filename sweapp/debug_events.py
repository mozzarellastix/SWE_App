from polls.models import Event, EventRSVP
from django.utils import timezone

print('All events:')
for e in Event.objects.all():
    is_future = e.date >= timezone.now()
    print(f'  Event {e.event_id}: {e.title} on {e.date} (future={is_future})')

print('\nAll RSVPs:')
for r in EventRSVP.objects.all():
    print(f'  User {r.user.username} -> Event {r.event.event_id} ({r.event.title}): {r.rsvp_status}')

print(f'\nCurrent time: {timezone.now()}')
