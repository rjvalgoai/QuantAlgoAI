from typing import Dict, List, Optional
import asyncio
from datetime import datetime
import structlog
from .ai_auto_debugger import AIAutoDebugger
from .quantum_debugger import QuantumDebugger
from core.logger import logger

class DebugManager:
    """Central debugging and monitoring system"""
    
    def __init__(self):
        self.ai_debugger = AIAutoDebugger()
        self.quantum_debugger = QuantumDebugger()
        self.logger = structlog.get_logger()
        self.system_state = {}
        self.error_counts = {}
        self.monitoring_active = False
        
    async def start_monitoring(self):
        """Start system monitoring"""
        try:
            self.monitoring_active = True
            while self.monitoring_active:
                await self.check_system_health()
                await asyncio.sleep(60)  # Check every minute
        except Exception as e:
            logger.error(f"Monitoring failed: {e}")
            
    async def check_system_health(self):
        """Check health of all system components"""
        try:
            # Get component states
            market_data_state = await self.check_market_data()
            trading_state = await self.check_trading_system()
            model_state = await self.check_ml_models()
            quantum_state = await self.check_quantum_system()
            
            # Update system state
            self.system_state = {
                "timestamp": datetime.now().isoformat(),
                "market_data": market_data_state,
                "trading": trading_state,
                "ml_models": model_state,
                "quantum": quantum_state,
                "overall_health": self._calculate_health_score([
                    market_data_state,
                    trading_state,
                    model_state,
                    quantum_state
                ])
            }
            
            # Log state
            self.logger.info("system_health_check", **self.system_state)
            
            # AI analysis of system state
            await self.ai_debugger.analyze_state(self.system_state)
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            
    async def handle_error(self, error: Exception, component: str):
        """Handle system errors"""
        try:
            # Update error counts
            self.error_counts[component] = self.error_counts.get(component, 0) + 1
            
            # Log error
            self.logger.error(f"component_error",
                component=component,
                error=str(error),
                error_count=self.error_counts[component]
            )
            
            # AI analysis of error
            analysis = await self.ai_debugger.analyze_error(error, component)
            
            # Take corrective action if needed
            if analysis.get("severity") == "high":
                await self._handle_critical_error(component, error, analysis)
                
        except Exception as e:
            logger.error(f"Error handling failed: {e}")
            
    async def _handle_critical_error(self, component: str, 
                                   error: Exception, 
                                   analysis: Dict):
        """Handle critical system errors"""
        try:
            # Stop affected component
            await self._stop_component(component)
            
            # Notify administrators
            await self._send_alert(component, error, analysis)
            
            # Attempt recovery
            if analysis.get("can_recover"):
                await self._attempt_recovery(component)
                
        except Exception as e:
            logger.error(f"Critical error handling failed: {e}")

debug_manager = DebugManager() 