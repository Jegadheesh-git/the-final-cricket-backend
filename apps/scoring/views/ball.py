from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from scoring.models.ball import Ball
from scoring.serializers.ball_input import BallInputSerializer
from scoring.services.ball_service import submit_ball, build_ball_outcome
from scoring.serializers.ball_outcome import BallOutcomeSerializer


class BallSubmissionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BallInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ball_id = submit_ball(
            serializer.validated_data,
            user=request.user
        )

        ball = Ball.objects.get(id=ball_id)
        outcome = build_ball_outcome(ball)

        response_serializer = BallOutcomeSerializer(outcome)

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
