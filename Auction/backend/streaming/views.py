import json
import time
import hmac
import hashlib
from django.conf import settings
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from auctions.models import Auction
from django.shortcuts import get_object_or_404

class AgoraTokenView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, auction_id):
        auction = get_object_or_404(Auction, id=auction_id)
        
        # Check if user is authorized to join the stream
        if not (request.user == auction.seller or request.user in auction.participants.all()):
            return Response({'error': 'Not authorized to join this stream'}, status=403)

        # Generate token
        app_id = settings.AGORA_APP_ID
        app_certificate = settings.AGORA_APP_CERTIFICATE
        channel_name = f'auction_{auction_id}'
        uid = request.user.id
        role = 1  # Publisher for seller, Subscriber for others
        expire_time = 3600  # 1 hour

        current_timestamp = int(time.time())
        privilege_expired_ts = current_timestamp + expire_time

        token = self._generate_token(
            app_id,
            app_certificate,
            channel_name,
            uid,
            role,
            privilege_expired_ts
        )

        return Response({
            'token': token,
            'app_id': app_id,
            'channel_name': channel_name,
            'uid': uid
        })

    def _generate_token(self, app_id, app_certificate, channel_name, uid, role, privilege_expired_ts):
        token = self._build_token_with_uid(
            app_id,
            app_certificate,
            channel_name,
            uid,
            role,
            privilege_expired_ts
        )
        return token

    def _build_token_with_uid(self, app_id, app_certificate, channel_name, uid, role, privilege_expired_ts):
        token = self._build_token(
            app_id,
            app_certificate,
            channel_name,
            uid,
            role,
            privilege_expired_ts
        )
        return token

    def _build_token(self, app_id, app_certificate, channel_name, uid, role, privilege_expired_ts):
        token = self._pack_uint16(1) + \
                self._pack_string(app_id) + \
                self._pack_uint32(privilege_expired_ts) + \
                self._pack_uint32(1) + \
                self._pack_uint32(privilege_expired_ts) + \
                self._pack_uint32(uid) + \
                self._pack_uint32(privilege_expired_ts) + \
                self._pack_string(channel_name)

        signature = hmac.new(
            app_certificate.encode('utf-8'),
            token,
            hashlib.sha256
        ).digest()

        return self._pack_uint16(len(signature)) + signature + token

    def _pack_uint16(self, x):
        return x.to_bytes(2, byteorder='big')

    def _pack_uint32(self, x):
        return x.to_bytes(4, byteorder='big')

    def _pack_string(self, string):
        return self._pack_uint16(len(string)) + string.encode('utf-8') 