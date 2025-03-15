from django.core.management.base import BaseCommand
from game.services.game_service import create_uno_rule_set

class Command(BaseCommand):
    help = 'Creates a UNO rule set'

    def add_arguments(self, parser):
        parser.add_argument('--direction', type=str, default='clockwise', help='Initial direction of play')
        parser.add_argument('--cards', type=int, default=7, help='Cards per player')
        parser.add_argument('--min', type=int, default=1, help='Minimum cards')
        parser.add_argument('--max', type=int, default=12, help='Maximum cards')

    def handle(self, *args, **options):
        rule_set = create_uno_rule_set(
            initial_direction=options['direction'],
            cards_per_player=options['cards'],
            min_cards=options['min'],
            max_cards=options['max']
        )
        self.stdout.write(self.style.SUCCESS(f'Successfully created UNO rule set with ID: {rule_set.uid}'))
