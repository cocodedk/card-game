from django.core.management.base import BaseCommand
from game.services.game_service_utils import create_idiot_rule_set

class Command(BaseCommand):
    help = 'Creates an Idiot card game rule set'

    def add_arguments(self, parser):
        parser.add_argument('--direction', type=str, default='counterclockwise', help='Initial direction of play')
        parser.add_argument('--cards', type=int, default=4, help='Cards per player')
        parser.add_argument('--min', type=int, default=2, help='Minimum cards')
        parser.add_argument('--max', type=int, default=8, help='Maximum cards')

    def handle(self, *args, **options):
        try:
            rule_set = create_idiot_rule_set(
                initial_direction=options['direction'],
                cards_per_player=options['cards'],
                min_cards=options['min'],
                max_cards=options['max']
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created Idiot card game rule set with ID: {rule_set.uid}'))
        except ValueError as e:
            self.stderr.write(self.style.ERROR(str(e)))
            self.stdout.write(self.style.ERROR('Failed to create rule set'))
