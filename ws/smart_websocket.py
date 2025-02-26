from __future__ import print_function
import struct
import ssl
import json
from websocket_client import WebSocket  # Import from websocket-client package
from core.logger import logger
import asyncio
from typing import Optional, Callable, Dict, Any

class SmartWebSocket:
    """SmartAPI WebSocket for Angel Broking"""
    
    ROOT_URI = "wss://smartapisocket.angelone.in/smart-stream"
    HEART_BEAT_MESSAGE = "ping"
    HEAR_BEAT_INTERVAL = 30
    LITTLE_ENDIAN_BYTE_ORDER = "<"
    RESUBSCRIBE_FLAG = False
    MAX_RETRY_ATTEMPT = 3
    CLOSE_CONNECTION = False

    # Available Actions
    SUBSCRIBE_ACTION = 1
    UNSUBSCRIBE_ACTION = 0

    # Subscription Modes
    LTP_MODE = 1
    QUOTE = 2
    SNAP_QUOTE = 3

    # Exchange Types
    NSE_CM = 1  # NSE Cash
    NSE_FO = 2  # NSE F&O
    BSE_CM = 3  # BSE Cash
    BSE_FO = 4  # BSE F&O
    MCX_FO = 5  # MCX F&O
    NCX_FO = 7  # NCX F&O
    CDE_FO = 13 # CDE F&O

    # Subscription Mode Map
    SUBSCRIPTION_MODE_MAP = {
        1: "LTP",
        2: "QUOTE",
        3: "SNAP_QUOTE"
    }

    def __init__(self, auth_token, api_key, client_code, feed_token):
        """Initialize SmartWebSocket"""
        self.auth_token = auth_token
        self.api_key = api_key
        self.client_code = client_code
        self.feed_token = feed_token
        self.wsapp = None
        self.input_request_dict = {}
        self.current_retry_attempt = 0
        self.connected = False
        self.reconnect_delay = 1

    def _on_data(self, wsapp, data, data_type, continue_flag):
        """Handle incoming data"""
        try:
            if data_type == 2:  # Binary data
                parsed_message = self._parse_binary_data(data)
                self.on_data(wsapp, parsed_message)
            else:  # Text data
                self.on_data(wsapp, data)
        except Exception as e:
            logger.error(f"Error processing websocket data: {e}")

    def _on_open(self, wsapp):
        """Handle WebSocket connection open"""
        try:
            logger.info("WebSocket connection opened")
            if self.RESUBSCRIBE_FLAG:
                self.resubscribe()
            else:
                self.RESUBSCRIBE_FLAG = True
                self.on_open(wsapp)
        except Exception as e:
            logger.error(f"Error in WebSocket open: {e}")

    def _on_pong(self, wsapp, data):
        print("In on pong function==> ", data)

    def _on_ping(self, wsapp, data):
        print("In on ping function==> ", data)

    def subscribe(self, correlation_id, mode, token_list):
        """Subscribe to market data"""
        try:
            request_data = {
                "correlationID": correlation_id,
                "action": self.SUBSCRIBE_ACTION,
                "params": {
                    "mode": mode,
                    "tokenList": token_list
                }
            }

            # Store subscription for reconnection
            if mode not in self.input_request_dict:
                self.input_request_dict[mode] = {}

            for token in token_list:
                if token['exchangeType'] in self.input_request_dict[mode]:
                    self.input_request_dict[mode][token['exchangeType']].extend(token["tokens"])
                else:
                    self.input_request_dict[mode][token['exchangeType']] = token["tokens"]

            self.wsapp.send(json.dumps(request_data))
            logger.info(f"Subscribed to {len(token_list)} symbols")
            
        except Exception as e:
            logger.error(f"Error subscribing to market data: {e}")
            raise

    def unsubscribe(self, correlation_id, mode, token_list):
        """Unsubscribe from market data"""
        try:
            request_data = {
                "correlationID": correlation_id,
                "action": self.UNSUBSCRIBE_ACTION,
                "params": {
                    "mode": mode,
                    "tokenList": token_list
                }
            }
            self.wsapp.send(json.dumps(request_data))
            logger.info(f"Unsubscribed from {len(token_list)} symbols")
        except Exception as e:
            logger.error(f"Error unsubscribing from market data: {e}")
            raise

    def connect(self):
        """Connect to WebSocket server"""
        try:
            headers = {
                'Authorization': self.auth_token,
                'x-api-key': self.api_key,
                'x-client-code': self.client_code,
                'x-feed-token': self.feed_token
            }
            
            self.wsapp = WebSocket(
                self.ROOT_URI,
                header=headers,
                on_open=self._on_open,
                on_error=self._on_error,
                on_close=self._on_close,
                on_data=self._on_data,
                on_ping=self._on_ping,
                on_pong=self._on_pong
            )
            
            self.wsapp.run_forever(
                sslopt={"cert_reqs": ssl.CERT_NONE},
                ping_interval=self.HEAR_BEAT_INTERVAL,
                ping_payload=self.HEART_BEAT_MESSAGE
            )
            
        except Exception as e:
            logger.error(f"Error connecting to WebSocket: {e}")
            raise

    def close_connection(self):
        """Close WebSocket connection"""
        try:
            self.CLOSE_CONNECTION = True
            self.RESUBSCRIBE_FLAG = False
            if self.wsapp:
                self.wsapp.close()
            logger.info("WebSocket connection closed")
        except Exception as e:
            logger.error(f"Error closing WebSocket connection: {e}")

    def _on_error(self, wsapp, error):
        """Handle WebSocket errors"""
        logger.error(f"WebSocket error: {error}")
        self.RESUBSCRIBE_FLAG = True
        if self.current_retry_attempt < self.MAX_RETRY_ATTEMPT and not self.CLOSE_CONNECTION:
            logger.info(f"Attempting reconnection {self.current_retry_attempt + 1}/{self.MAX_RETRY_ATTEMPT}")
            self.current_retry_attempt += 1
            self.connect()

    def _on_close(self, wsapp, close_status_code, close_msg):
        """Handle WebSocket connection close"""
        logger.info(f"WebSocket connection closed: {close_status_code} - {close_msg}")
        self.on_close(wsapp)

    def _parse_binary_data(self, binary_data):
        """Parse binary market data"""
        try:
            parsed_data = {
                "subscription_mode": self._unpack_data(binary_data, 0, 1, byte_format="B")[0],
                "exchange_type": self._unpack_data(binary_data, 1, 2, byte_format="B")[0],
                "token": self._parse_token_value(binary_data[2:27]),
                "sequence_number": self._unpack_data(binary_data, 27, 35, byte_format="q")[0],
                "exchange_timestamp": self._unpack_data(binary_data, 35, 43, byte_format="q")[0],
                "last_traded_price": self._unpack_data(binary_data, 43, 51, byte_format="q")[0]
            }

            parsed_data["subscription_mode_val"] = self.SUBSCRIPTION_MODE_MAP.get(parsed_data["subscription_mode"])
            return parsed_data
            
        except Exception as e:
            logger.error(f"Error parsing binary data: {e}")
            raise

    def _unpack_data(self, binary_data, start, end, byte_format="I"):
        """Unpack binary data using struct"""
        return struct.unpack(self.LITTLE_ENDIAN_BYTE_ORDER + byte_format, binary_data[start:end])

    @staticmethod
    def _parse_token_value(binary_packet):
        """Parse token value from binary packet"""
        token = ""
        for i in range(len(binary_packet)):
            if chr(binary_packet[i]) == '\x00':
                return token
            token += chr(binary_packet[i])
        return token

    # Callback methods to be overridden by user
    def on_data(self, wsapp, data):
        """Handle market data updates"""
        pass

    def on_close(self, wsapp):
        """Handle connection close"""
        pass

    def on_open(self, wsapp):
        """Handle connection open"""
        pass

    def resubscribe(self):
        """Resubscribe to previous subscriptions after reconnect"""
        try:
            for mode, exchanges in self.input_request_dict.items():
                token_list = []
                for exchange_type, tokens in exchanges.items():
                    token_list.append({
                        'exchangeType': exchange_type,
                        'tokens': tokens
                    })
                request_data = {
                    "action": self.SUBSCRIBE_ACTION,
                    "params": {
                        "mode": mode,
                        "tokenList": token_list
                    }
                }
                self.wsapp.send(json.dumps(request_data))
                logger.info(f"Resubscribed to {len(token_list)} symbols")
        except Exception as e:
            logger.error(f"Error resubscribing: {e}")
            raise