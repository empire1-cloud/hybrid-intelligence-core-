import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const APPROVED_PIPELINE_MODEL = "gpt-4o-mini";

const AVAILABLE_ENGINES = [
  { id: "strategy_engine", name: "Strategy Engine", tone: "gold", desc: "Generate high-level strategies" },
  { id: "plan_builder_engine", name: "Plan Builder Engine", tone: "gold", desc: "Convert goals to execution plans" },
  { id: "analysis_engine", name: "Analysis Engine", tone: "gold", desc: "Deep SWOT analysis" },
  { id: "opportunity_mapper_engine", name: "Opportunity Mapper Engine", tone: "gold", desc: "Identify opportunities" },
  { id: "evaluator_engine", name: "Evaluator Engine", tone: "gold", desc: "Score and evaluate" },
  { id: "pricing_engine", name: "Pricing Engine", tone: "gold", desc: "Generate pricing structures" },
  { id: "blueprint_engine", name: "Blueprint Engine", tone: "gold", desc: "System architecture" },
  { id: "money_pipeline_engine", name: "Money Pipeline Engine", tone: "gold", desc: "Full monetization" },
  { id: "persona_engine", name: "Persona Engine", tone: "pink", desc: "User personas" },
  { id: "anime_character_engine", name: "Anime Character Engine", tone: "pink", desc: "Create anime characters" },
  { id: "anime_lore_engine", name: "Anime Lore Engine", tone: "pink", desc: "World-building" },
  { id: "anime_story_engine", name: "Anime Story Engine", tone: "pink", desc: "Story arcs" },
  { id: "art_direction_engine", name: "Art Direction Engine", tone: "pink", desc: "Visual direction" },
];

const PRESET_PIPELINES = {
  business_plan: { name: "Full Business Plan", description: "Strategy → Analysis → Opportunities → Plan → Pricing", steps: [{ engine: "strategy_engine", input_key: "goal", output_key: "strategy" }, { engine: "analysis_engine", input_key: "strategy.summary", output_key: "analysis" }, { engine: "opportunity_mapper_engine", input_key: "analysis", output_key: "opportunities" }, { engine: "plan_builder_engine", input_key: "strategy", output_key: "plan" }, { engine: "pricing_engine", input_key: "strategy.summary", output_key: "pricing" }] },
  startup_validation: { name: "Startup Validation", description: "Analysis → Persona → Opportunities → Evaluation", steps: [{ engine: "analysis_engine", input_key: "business_idea", output_key: "market_analysis" }, { engine: "persona_engine", input_key: "target_customer", output_key: "icp" }, { engine: "opportunity_mapper_engine", input_key: "market", output_key: "opportunities" }, { engine: "evaluator_engine", input_key: "business_idea", output_key: "viability" }] },
  idea_to_money: { name: "Idea to Money", description: "Money Pipeline → Persona → Blueprint → Evaluation", steps: [{ engine: "money_pipeline_engine", input_key: "idea", output_key: "pipeline" }, { engine: "persona_engine", input_key: "pipeline.market_analysis", output_key: "personas" }, { engine: "blueprint_engine", input_key: "pipeline.product_blueprint", output_key: "architecture" }, { engine: "evaluator_engine", input_key: "pipeline", output_key: "assessment" }] },
  anime_concept: { name: "Anime Full Concept", description: "Lore → Story → Character → Art Direction", steps: [{ engine: "anime_lore_engine", input_key: "world_concept", output_key: "lore" }, { engine: "anime_story_engine", input_key: "lore", output_key: "story" }, { engine: "anime_character_engine", input_key: "story.premise", output_key: "protagonist" }, { engine: "art_direction_engine", input_key: "story,lore", output_key: "art_direction" }] },
  product_launch: { name: "Product Launch", description: "Persona → Strategy → Pricing → Plan", steps: [{ engine: "persona_engine", input_key: "audience", output_key: "personas" }, { engine: "strategy_engine", input_key: "product_goal", output_key: "strategy" }, { engine: "pricing_engine", input_key: "product", output_key: "pricing" }, { engine: "plan_builder_engine", input_key: "strategy", output_key: "launch_plan" }] },
};

const STATUS_LABELS = { queued: "QUEUED", running: "RUNNING", done: "DONE", error: "FAILED" };

const PipelineComposerPage = () => {
  const { authAxios } = useAuth();
  const [steps, setSteps] = useState([]);
  const [initialInput, setInitialInput] = useState("");
  const [executing, setExecuting] = useState(false);
  const [currentStep, setCurrentStep] = useState(-1);
  const [results, setResults] = useState([]);
  const [savedPipelines, setSavedPipelines] = useState({});
  const [pipelineName, setPipelineName] = useState("");
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [showLoadModal, setShowLoadModal] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem("savedPipelines");
    if (saved) setSavedPipelines(JSON.parse(saved));
  }, []);

  const addStep = (engine) => {
    const engineInfo = AVAILABLE_ENGINES.find((item) => item.id === engine);
    setSteps([...steps, { id: Date.now(), engine, name: engineInfo?.name || engine, tone: engineInfo?.tone || "gold", input_key: steps.length === 0 ? "input" : `step_${steps.length}`, output_key: `step_${steps.length + 1}` }]);
  };

  const removeStep = (index) => setSteps(steps.filter((_, itemIndex) => itemIndex !== index));
  const moveStep = (index, direction) => {
    const nextSteps = [...steps];
    const nextIndex = index + direction;
    if (nextIndex < 0 || nextIndex >= steps.length) return;
    [nextSteps[index], nextSteps[nextIndex]] = [nextSteps[nextIndex], nextSteps[index]];
    setSteps(nextSteps);
  };

  const loadPreset = (presetKey) => {
    const preset = PRESET_PIPELINES[presetKey];
    if (!preset) return;
    setSteps(preset.steps.map((step, index) => {
      const engineInfo = AVAILABLE_ENGINES.find((item) => item.id === step.engine);
      return { id: Date.now() + index, engine: step.engine, name: engineInfo?.name || step.engine, tone: engineInfo?.tone || "gold", input_key: step.input_key, output_key: step.output_key };
    }));
    setShowLoadModal(false);
  };

  const loadSavedPipeline = (key) => {
    const pipeline = savedPipelines[key];
    if (!pipeline) return;
    setSteps(pipeline.steps);
    setShowLoadModal(false);
  };

  const savePipeline = () => {
    if (!pipelineName.trim() || steps.length === 0) return;
    const nextSaved = { ...savedPipelines, [pipelineName]: { name: pipelineName, steps, createdAt: new Date().toISOString() } };
    setSavedPipelines(nextSaved);
    localStorage.setItem("savedPipelines", JSON.stringify(nextSaved));
    setPipelineName("");
    setShowSaveModal(false);
  };

  const deleteSavedPipeline = (key) => {
    const nextSaved = { ...savedPipelines };
    delete nextSaved[key];
    setSavedPipelines(nextSaved);
    localStorage.setItem("savedPipelines", JSON.stringify(nextSaved));
  };

  const getEnginePayload = (engine, input, previousResults) => {
    const basePayload = { model: APPROVED_PIPELINE_MODEL };
    const context = JSON.stringify(previousResults).slice(0, 500);
    switch (engine) {
      case "strategy_engine": return { ...basePayload, goal: input, context };
      case "plan_builder_engine": return { ...basePayload, goal: input, strategy: previousResults[previousResults.length - 1]?.output };
      case "analysis_engine": return { ...basePayload, subject: input, context };
      case "opportunity_mapper_engine": return { ...basePayload, situation: input, context };
      case "evaluator_engine": return { ...basePayload, subject: "Pipeline Output", content: input, criteria_preset: "idea" };
      case "pricing_engine": return { ...basePayload, product: input, target_market: "General market" };
      case "blueprint_engine": return { ...basePayload, system_description: input };
      case "persona_engine": return { ...basePayload, audience: input, context };
      case "anime_character_engine": return { ...basePayload, concept: input, genre: "fantasy" };
      case "anime_lore_engine": return { ...basePayload, world_concept: input };
      case "anime_story_engine": return { ...basePayload, concept: input, episode_count: 12 };
      case "art_direction_engine": return { ...basePayload, project: input, genre: "anime" };
      case "money_pipeline_engine": return { ...basePayload, idea: input };
      default: return { ...basePayload, input };
    }
  };

  const getEngineEndpoint = (engine) => ({ strategy_engine: "/strategy", plan_builder_engine: "/plan", analysis_engine: "/analyze", opportunity_mapper_engine: "/opportunities", evaluator_engine: "/evaluate", pricing_engine: "/pricing", blueprint_engine: "/blueprint", persona_engine: "/persona", anime_character_engine: "/anime/character", anime_lore_engine: "/anime/lore", anime_story_engine: "/anime/story", art_direction_engine: "/art-direction", money_pipeline_engine: "/money-pipeline" }[engine] || `/${engine}`);

  const executePipeline = async () => {
    if (steps.length === 0 || !initialInput.trim()) return;
    setExecuting(true);
    setResults([]);
    setCurrentStep(0);

    const pipelineResults = [];
    let currentInput = initialInput;

    for (let index = 0; index < steps.length; index += 1) {
      setCurrentStep(index);
      const step = steps[index];
      const stepResult = { step: index + 1, engine: step.engine, name: step.name, tone: step.tone, input: currentInput, output: null, error: null, duration: 0, status: "running" };
      setResults([...pipelineResults, stepResult]);
      const startTime = Date.now();

      try {
        const response = await authAxios().post(getEngineEndpoint(step.engine), getEnginePayload(step.engine, currentInput, pipelineResults), { timeout: 120000 });
        stepResult.output = response.data;
        stepResult.status = "success";
        stepResult.duration = Date.now() - startTime;
        currentInput = response.data.summary || response.data.objective || response.data.core_offer || response.data.name || JSON.stringify(response.data).slice(0, 500);
      } catch (error) {
        stepResult.error = error.response?.data?.detail || error.message;
        stepResult.status = "error";
        stepResult.duration = Date.now() - startTime;
      }

      pipelineResults.push(stepResult);
      setResults([...pipelineResults]);
      if (stepResult.status === "error") break;
    }

    setCurrentStep(-1);
    setExecuting(false);
  };

  const clearPipeline = () => { setSteps([]); setResults([]); setInitialInput(""); };

  const engineCounts = steps.reduce((counts, step) => ({ ...counts, [step.engine]: (counts[step.engine] || 0) + 1 }), {});

  const stepStatus = (index) => {
    const result = results[index];
    if (!result) return "queued";
    if (result.status === "success") return "done";
    if (result.status === "error") return "error";
    return "running";
  };

  const allDone = steps.length > 0 && results.length === steps.length && results.every((result) => result.status === "success");
  const failed = results.find((result) => result.status === "error");

  let runStatusText = "ADD ENGINES TO BUILD YOUR PIPELINE";
  if (steps.length > 0) {
    if (executing && currentStep >= 0) {
      runStatusText = `RUNNING STEP ${currentStep + 1} OF ${steps.length}: ${(steps[currentStep]?.name || "").toUpperCase()}`;
    } else if (failed) {
      runStatusText = `PIPELINE HALTED AT STEP ${failed.step} — ${failed.name.toUpperCase()}`;
    } else if (allDone) {
      runStatusText = `PIPELINE COMPLETE — ${steps.length} STEP${steps.length > 1 ? "S" : ""} EXECUTED`;
    } else if (!initialInput.trim()) {
      runStatusText = `${steps.length} STEP${steps.length > 1 ? "S" : ""} STAGED — AWAITING INITIAL INPUT`;
    } else {
      runStatusText = `${steps.length} STEP${steps.length > 1 ? "S" : ""} READY TO RUN`;
    }
  }

  const runDisabled = executing || steps.length === 0 || !initialInput.trim();

  return (
    <div className="composer-page" data-testid="pipeline-composer-page">
      <header className="composer-hero">
        <Link to="/" className="composer-back">← Home</Link>
        <div className="composer-eyebrow">WORKFLOW ORCHESTRATION</div>
        <h1>Pipeline Composer</h1>
        <p>Chain multiple engines together for complex, sequenced workflows. Each executed step uses one monthly execution.</p>
      </header>

      <div className="composer-layout">
        <aside className="composer-panel composer-sidebar">
          <div className="panel-label">Available Engines</div>
          <div className="panel-hint">Click to add to pipeline</div>
          <div className="engine-selector" data-testid="engine-selector">
            {AVAILABLE_ENGINES.map((engine) => (
              <button
                key={engine.id}
                type="button"
                className="engine-row"
                onClick={() => addStep(engine.id)}
                disabled={executing}
                title={engine.desc}
                data-testid={`add-engine-${engine.id}`}
              >
                <span className={`engine-tone engine-tone-${engine.tone}`} />
                <span className="engine-row-name">{engine.name}</span>
                {engineCounts[engine.id] > 0 && <span className="engine-badge">×{engineCounts[engine.id]}</span>}
              </button>
            ))}
          </div>

          <div className="panel-label panel-label-spaced">Presets &amp; Saved</div>
          <div className="preset-buttons">
            <button type="button" className="preset-btn" onClick={() => setShowLoadModal(true)} data-testid="load-btn">Load Pipeline</button>
            <button type="button" className="preset-btn" onClick={() => setShowSaveModal(true)} disabled={steps.length === 0} data-testid="save-btn">Save Pipeline</button>
          </div>
        </aside>

        <main className="composer-panel composer-main">
          <div className="builder-header">
            <div className="panel-label">Pipeline Steps ({steps.length})</div>
            <button type="button" className="clear-btn" onClick={clearPipeline} disabled={executing || steps.length === 0}>CLEAR ALL</button>
          </div>

          {steps.length === 0 ? (
            <div className="empty-pipeline">Add engines from the left panel to build your pipeline</div>
          ) : (
            <div className="pipeline-steps" data-testid="pipeline-steps">
              {steps.map((step, index) => {
                const status = stepStatus(index);
                return (
                  <div className={`pipeline-step pipeline-step-${status}`} key={step.id}>
                    <span className="step-index">{index + 1}</span>
                    <span className="step-name">{step.name}</span>
                    <span className={`step-status step-status-${status}`}>{STATUS_LABELS[status]}</span>
                    <span className={`status-dot status-dot-${status}`} />
                    <span className="step-actions">
                      <button type="button" onClick={() => moveStep(index, -1)} disabled={index === 0 || executing} title="Move up">↑</button>
                      <button type="button" onClick={() => moveStep(index, 1)} disabled={index === steps.length - 1 || executing} title="Move down">↓</button>
                      <button type="button" className="step-remove" onClick={() => removeStep(index)} disabled={executing} title="Remove">×</button>
                    </span>
                  </div>
                );
              })}
            </div>
          )}

          <div className="pipeline-input-section">
            <label className="panel-label" htmlFor="initial-input">Initial Input</label>
            <textarea
              id="initial-input"
              value={initialInput}
              onChange={(event) => setInitialInput(event.target.value)}
              placeholder="Enter the starting input for your pipeline (e.g., 'Build an AI-powered fitness app')"
              rows={3}
              disabled={executing}
              data-testid="initial-input"
            />
          </div>

          <div className="composer-runbar">
            <div className="run-status">{runStatusText}</div>
            <button type="button" className="run-btn" onClick={executePipeline} disabled={runDisabled} data-testid="execute-btn">
              {executing ? <><span className="btn-spinner" /> RUNNING…</> : "RUN PIPELINE"}
            </button>
          </div>
        </main>
      </div>

      {results.length > 0 && (
        <section className="results-timeline" data-testid="results-timeline">
          <div className="panel-label">Execution Timeline</div>
          <div className="timeline">
            {results.map((result, index) => (
              <div key={index} className={`timeline-item ${result.status}`} data-testid={`timeline-item-${index}`}>
                <div className="timeline-marker">
                  {result.status === "running" ? <span className="marker-spinner" /> : result.status === "success" ? <span className="marker-success">✓</span> : <span className="marker-error">✗</span>}
                </div>
                <div className="timeline-content">
                  <div className="timeline-header">
                    <span className="timeline-step">STEP {result.step}</span>
                    <span className="timeline-engine">{result.name}</span>
                    {result.duration > 0 && <span className="timeline-duration">{(result.duration / 1000).toFixed(1)}s</span>}
                  </div>
                  <div className="timeline-io">
                    <details className="io-section">
                      <summary>Input</summary>
                      <pre>{typeof result.input === "string" ? result.input : JSON.stringify(result.input, null, 2)}</pre>
                    </details>
                    {result.output && (
                      <details className="io-section" open={index === results.length - 1}>
                        <summary>Output</summary>
                        <pre>{JSON.stringify(result.output, null, 2)}</pre>
                      </details>
                    )}
                    {result.error && <div className="io-error"><strong>Error:</strong> {result.error}</div>}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {showSaveModal && (
        <div className="modal-overlay" onClick={() => setShowSaveModal(false)}>
          <div className="modal-content modal-small" onClick={(event) => event.stopPropagation()}>
            <div className="modal-header"><h2>Save Pipeline</h2><button className="modal-close" onClick={() => setShowSaveModal(false)}>×</button></div>
            <div className="modal-body">
              <div className="form-group">
                <label>Pipeline Name</label>
                <input type="text" value={pipelineName} onChange={(event) => setPipelineName(event.target.value)} placeholder="My Custom Pipeline" data-testid="pipeline-name-input" />
              </div>
              <div className="save-preview"><p><strong>Steps:</strong> {steps.map((step) => step.name).join(" → ")}</p></div>
              <button className="btn-submit" onClick={savePipeline} disabled={!pipelineName.trim()} data-testid="confirm-save-btn">Save Pipeline</button>
            </div>
          </div>
        </div>
      )}

      {showLoadModal && (
        <div className="modal-overlay" onClick={() => setShowLoadModal(false)}>
          <div className="modal-content" onClick={(event) => event.stopPropagation()}>
            <div className="modal-header"><h2>Load Pipeline</h2><button className="modal-close" onClick={() => setShowLoadModal(false)}>×</button></div>
            <div className="modal-body">
              <h4>Preset Pipelines</h4>
              <div className="preset-list">
                {Object.entries(PRESET_PIPELINES).map(([key, preset]) => (
                  <div key={key} className="preset-item" onClick={() => loadPreset(key)} data-testid={`preset-${key}`}>
                    <div className="preset-info"><strong>{preset.name}</strong><p>{preset.description}</p></div>
                    <button className="btn-small btn-primary">Load</button>
                  </div>
                ))}
              </div>
              {Object.keys(savedPipelines).length > 0 && (
                <>
                  <h4>Saved Pipelines</h4>
                  <div className="preset-list">
                    {Object.entries(savedPipelines).map(([key, pipeline]) => (
                      <div key={key} className="preset-item">
                        <div className="preset-info"><strong>{pipeline.name}</strong><p>{pipeline.steps.map((step) => step.name).join(" → ")}</p></div>
                        <div className="preset-actions">
                          <button className="btn-small btn-primary" onClick={() => loadSavedPipeline(key)}>Load</button>
                          <button className="btn-small btn-danger" onClick={() => deleteSavedPipeline(key)}>Delete</button>
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PipelineComposerPage;
