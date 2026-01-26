from scoring.engine.rebuild_engine import rebuild_innings_state
from scoring.models.aggregates import InningsAggregate


def rebuild_innings(innings):
    rebuild_innings_state(innings)

def apply_dls_override(innings, target, overs):
    aggregate = InningsAggregate.objects.get(innings=innings)

    aggregate.revised_target_runs = target
    aggregate.max_overs = overs
    aggregate.save()
