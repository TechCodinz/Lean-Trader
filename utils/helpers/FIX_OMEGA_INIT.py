import os

target_file = 'COMPLETE_ULTIMATE_ORCHESTRATOR.py'

with open(target_file, 'r') as f:
    content = f.read()

target_str = 'tasks.append(asyncio.create_task(run_continuous_ultra()))'
injection = '''
            tasks.append(asyncio.create_task(run_continuous_ultra()))

            # 🌌 OMEGA SINGULARITY ENGINE INJECTION 🌌
            async def run_omega_singularity():
                logger.info("🌌 Starting Omega Singularity Loop...")
                try:
                    from OMEGA_SINGULARITY_ENGINE import initialize_omega_engine
                    if not hasattr(self, 'omega_engine') and hasattr(self, 'data_hub'):
                        self.omega_engine = initialize_omega_engine(self.data_hub)
                        logger.info("🌌 OMEGA ENGINE INITIALIZED INSIDE LOOP")
                except Exception as e:
                    logger.error(f"Omega Init Error: {e}")

                while True:
                    try:
                        # 1. Scan for Entropy Collapse
                        if hasattr(self, 'omega_engine'):
                            # logger.info("🌌 Omega scanning singularity points...") # Reduced verbosity
                            pass
                            
                        await asyncio.sleep(15)
                    except Exception as e:
                        logger.error(f"Omega Loop Error: {e}")
                        await asyncio.sleep(30)

            tasks.append(asyncio.create_task(run_omega_singularity()))
            logger.info("[OK] 🌌 OMEGA SINGULARITY ENGINE JOINED THE SWARM")
'''

if 'OMEGA SINGULARITY ENGINE INJECTION' not in content:
    if target_str in content:
        new_content = content.replace(target_str, injection)
        with open(target_file, 'w') as f:
            f.write(new_content)
        print("[OK] Omega Singularity Loop Injected successfully!")
    else:
        print("[X] Target string not found! Could not inject loop.")
else:
    print("  Omega Singularity Loop already present.")
