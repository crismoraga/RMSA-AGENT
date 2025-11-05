"""Live demo runner comparing 4 RMSA agents with ultra visualization.""""""Live demo runner comparing multiple RMSA agents (up to 6)."""

from __future__ import annotationsfrom __future__ import annotations



from pathlib import Pathfrom pathlib import Path

from typing import Generator, Iterable, List, Tuplefrom typing import Generator, Iterable, Tuple



from stable_baselines3 import PPOfrom stable_baselines3 import PPO



from agents import AgentBuilderfrom agents import AgentBuilder

from config import (from config import (

    DEFAULT_AGENT_CONFIG,    DEFAULT_AGENT_CONFIG,

    DEFAULT_TRAINING,    DEFAULT_TRAINING,

    DEMO,    DEMO,

    ENVIRONMENT,    ENVIRONMENT,

    OPTIMIZED_AGENT_CONFIG,    OPTIMIZED_AGENT_CONFIG,

    OPTIMIZED_TRAINING,    OPTIMIZED_TRAINING,

    DEEP_QOT_AGENT_CONFIG,    DEEP_QOT_AGENT_CONFIG,

    DEEP_QOT_TRAINING,    DEEP_QOT_TRAINING,

    ADAPTIVE_AGENT_CONFIG,    ADAPTIVE_AGENT_CONFIG,

    ADAPTIVE_TRAINING,    ADAPTIVE_TRAINING,

    REWARD_WEIGHTS,    REWARD_WEIGHTS,

))

from environment import EnvironmentFactory, RMSAEnvironmentWrapperfrom environment import EnvironmentFactory, RMSAEnvironmentWrapper

from metrics import MetricsTrackerfrom metrics import MetricsTracker

from reward_functions import build_reward_functionfrom reward_functions import build_reward_function

from ultra_visualizer import AgentSnapshot, MultiAgentSnapshot, UltraVisualizerfrom ultra_visualizer import AgentSnapshot, MultiAgentSnapshot, UltraVisualizer





def _load_model_or_raise(path: str) -> PPO:def _load_model_or_raise(path: str) -> PPO:

    resolved = Path(path)    resolved = Path(path)

    if not resolved.exists():    if not resolved.exists():

        raise FileNotFoundError(f"Model not found at {resolved}. Please train agents first.")        raise FileNotFoundError(f"Model checkpoint not found: {resolved}")

    return PPO.load(resolved)    return PPO.load(resolved)





def _prepare_agent(def _prepare_agent(

    builder: AgentBuilder,    builder: AgentBuilder,

    checkpoint: str,    checkpoint: str,

    seed: int,    seed: int,

) -> Tuple[PPO, RMSAEnvironmentWrapper, MetricsTracker]:) -> Tuple[PPO, RMSAEnvironmentWrapper, MetricsTracker]:

    model = _load_model_or_raise(checkpoint)    model = _load_model_or_raise(checkpoint)

    tracker = MetricsTracker()    tracker = MetricsTracker()

    env = RMSAEnvironmentWrapper(    env = RMSAEnvironmentWrapper(

        factory=builder.factory,        factory=builder.factory,

        reward_fn=builder.reward_fn,        reward_fn=builder.reward_fn,

        seed=seed,        seed=seed,

    )    )

    env.reset()    env.reset()

    return model, env, tracker    return model, env, tracker





def _snapshot_from(def _snapshot_from(

    name: str,    name: str,

    step: int,    step: int,

    shaped_reward: float,    shaped_reward: float,

    info: dict,    info: dict,

    tracker: MetricsTracker,    tracker: MetricsTracker,

) -> AgentSnapshot:) -> AgentSnapshot:

    metrics = tracker.snapshot()    metrics = tracker.snapshot()

    last_action = info.get("action_label") or info.get("path") or ""    last_action = info.get("action_label") or info.get("path") or ""

    return AgentSnapshot(    return AgentSnapshot(

        name=name,        name=name,

        step=step,        step=step,

        shaped_reward=shaped_reward,        shaped_reward=shaped_reward,

        metrics=metrics,        metrics=metrics,

        last_action=str(last_action),        last_action=str(last_action),

    )    )





def _episode_stream_multi(def _episode_stream_multi(

    agents_data: List[Tuple[PPO, RMSAEnvironmentWrapper, MetricsTracker, str]],    agents_data: list,  # List of (model, env, tracker, config, training) tuples

    max_requests: int,    max_requests: int,

    episode_id: int,    episode_id: int,

) -> Generator[MultiAgentSnapshot, None, None]:) -> Generator[MultiAgentSnapshot, None, None]:

    """    default_obs, default_info = default_env.reset()

    Stream snapshots for multiple agents (currently 4: control, optimized, deep_qot, adaptive).    optimized_obs, optimized_info = optimized_env.reset()

    

    Args:    for request_idx in range(1, max_requests + 1):

        agents_data: List of (model, env, tracker, name) tuples        default_action, _ = default_model.predict(default_obs, deterministic=True)

        max_requests: Number of connection requests to process        optimized_action, _ = optimized_model.predict(optimized_obs, deterministic=True)

        episode_id: Current episode number

    """        default_obs, default_reward, default_term, default_trunc, default_info = default_env.step(

    # Reset all environments            default_action

    observations = []        )

    for model, env, tracker, name in agents_data:        optimized_obs, optimized_reward, opt_term, opt_trunc, optimized_info = optimized_env.step(

        obs, info = env.reset()            optimized_action

        observations.append(obs)        )

    

    for request_idx in range(1, max_requests + 1):        default_tracker.update(default_info)

        # Get actions from all agents        optimized_tracker.update(optimized_info)

        actions = []

        for idx, (model, env, tracker, name) in enumerate(agents_data):        connection_label = optimized_info.get("connection_label") or default_info.get(

            action, _ = model.predict(observations[idx], deterministic=True)            "connection_label", ""

            actions.append(action)        )

        

        # Step all environments        yield DemoSnapshot(

        step_results = []            episode=episode_id,

        for idx, (model, env, tracker, name) in enumerate(agents_data):            request_id=request_idx,

            obs, reward, terminated, truncated, info = env.step(actions[idx])            default_agent=_snapshot_from(

            observations[idx] = obs                DEFAULT_AGENT_CONFIG.name,

            tracker.update(info)                request_idx,

            step_results.append((reward, info))                default_reward,

                        default_info,

        # Get connection label from any agent (should be same for all with fairness seed)                default_tracker,

        connection_label = step_results[0][1].get("connection_label", "")            ),

                    optimized_agent=_snapshot_from(

        # Create snapshots for all 4 agents                OPTIMIZED_AGENT_CONFIG.name,

        snapshots = []                request_idx,

        for idx, (model, env, tracker, name) in enumerate(agents_data):                optimized_reward,

            reward, info = step_results[idx]                optimized_info,

            snapshot = _snapshot_from(name, request_idx, reward, info, tracker)                optimized_tracker,

            snapshots.append(snapshot)            ),

                    connection_label=str(connection_label),

        # Yield MultiAgentSnapshot with all 4 agents        )

        yield MultiAgentSnapshot(

            episode=episode_id,        if default_term or default_trunc or opt_term or opt_trunc:

            request_id=request_idx,            break

            control_agent=snapshots[0],

            optimized_agent=snapshots[1],

            deep_qot_agent=snapshots[2],def demo_stream(episodes: int = 1) -> Iterable[DemoSnapshot]:

            adaptive_agent=snapshots[3],    factory = EnvironmentFactory(base_kwargs=ENVIRONMENT.as_dict())

            connection_label=str(connection_label),

            topology=ENVIRONMENT.topology,    default_builder = AgentBuilder(

        )        config=DEFAULT_AGENT_CONFIG,

                factory=factory,

        # Check if any environment is done        reward_fn=build_reward_function(

        if any(step_results[i][1].get("terminated", False) or step_results[i][1].get("truncated", False)             DEFAULT_AGENT_CONFIG.reward_id, REWARD_WEIGHTS.get(DEFAULT_AGENT_CONFIG.reward_id, {})

               for i in range(len(agents_data))):        ),

            break    )

    optimized_builder = AgentBuilder(

        config=OPTIMIZED_AGENT_CONFIG,

def demo_stream_multi(episodes: int = 1) -> Iterable[MultiAgentSnapshot]:        factory=factory,

    """Main demo stream for 4 agents."""        reward_fn=build_reward_function(

    factory = EnvironmentFactory(base_kwargs=ENVIRONMENT.as_dict())            OPTIMIZED_AGENT_CONFIG.reward_id, REWARD_WEIGHTS.get(OPTIMIZED_AGENT_CONFIG.reward_id, {})

            ),

    # Build all 4 agents    )

    builders = [

        (DEFAULT_AGENT_CONFIG, DEFAULT_TRAINING, DEMO.fairness_seed),    default_model, default_env, default_tracker = _prepare_agent(

        (OPTIMIZED_AGENT_CONFIG, OPTIMIZED_TRAINING, DEMO.fairness_seed + 7),        default_builder, DEFAULT_TRAINING.save_path, DEMO.fairness_seed

        (DEEP_QOT_AGENT_CONFIG, DEEP_QOT_TRAINING, DEMO.fairness_seed + 13),    )

        (ADAPTIVE_AGENT_CONFIG, ADAPTIVE_TRAINING, DEMO.fairness_seed + 19),    optimized_model, optimized_env, optimized_tracker = _prepare_agent(

    ]        optimized_builder, OPTIMIZED_TRAINING.save_path, DEMO.fairness_seed + 7

        )

    agents_data = []

    for config, training, seed in builders:    for episode in range(1, episodes + 1):

        builder = AgentBuilder(        default_tracker.reset()

            config=config,        optimized_tracker.reset()

            factory=factory,        yield from _episode_stream(

            reward_fn=build_reward_function(            default_model,

                config.reward_id, REWARD_WEIGHTS.get(config.reward_id, {})            optimized_model,

            ),            default_env,

        )            optimized_env,

        model, env, tracker = _prepare_agent(builder, training.save_path, seed)            default_tracker,

        agents_data.append((model, env, tracker, config.name))            optimized_tracker,

                DEMO.demo_requests,

    # Run episodes            episode,

    for episode in range(1, episodes + 1):        )

        # Reset all trackers

        for model, env, tracker, name in agents_data:

            tracker.reset()def main() -> None:

            visualizer = LiveVisualizer(refresh_hz=DEMO.refresh_hz)

        yield from _episode_stream_multi(    visualizer.run(demo_stream())

            agents_data,

            DEMO.demo_requests,

            episode,if __name__ == "__main__":

        )    main()

    
    # Cleanup
    for model, env, tracker, name in agents_data:
        env.close()


def main() -> None:
    visualizer = UltraVisualizer(refresh_hz=DEMO.refresh_hz)
    visualizer.run(demo_stream_multi())


if __name__ == "__main__":
    main()
