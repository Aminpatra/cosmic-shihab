import { Info } from 'lucide-react'
import { useApi } from '../api.js'
import { LoadError, Loading } from './ApiState.jsx'
import './FlexModel.css'

// The FLEX test-outcome model (#16), shown from GET /api/flex-model exactly as stored. Every number
// here comes from that file; the notice and the limitations are always shown with the scores.

const MODEL_NAMES = {
  baseline: 'Majority-class baseline',
  logistic_regression: 'Logistic regression',
  random_forest: 'Random forest',
}
const FEATURE_NAMES = {
  fuel_heptane: 'Fuel is heptane',
  pressure: 'Pressure',
  oxygen: 'Oxygen',
  co2: 'CO₂',
  helium: 'Helium',
  droplet_diameter: 'Droplet diameter',
}
const DIRECTION = { toward: 'toward', away: 'away', mixed: 'mixed' }

const f3 = (v) => v.toFixed(3)

function Scores({ model }) {
  const order = ['baseline', 'logistic_regression', 'random_forest']
  return (
    <div className="fm-scores">
      <ul className="fm-bars" aria-label="Macro-F1 on the held-out test days, 0 to 1">
        {order.map((key) => {
          const held = model.held_out[key].macro_f1
          const cv = model.cross_validation.scores[key]
          const chosen = key === model.chosen_model
          return (
            <li key={key} className={chosen ? 'fm-bar fm-chosen' : 'fm-bar'}>
              <span className="fm-bar-name">
                {MODEL_NAMES[key]}
                {chosen && <span className="fm-tag">chosen beforehand</span>}
              </span>
              <span className="fm-bar-track" aria-hidden="true">
                <span className="fm-bar-fill" style={{ '--v': held }} />
                <span className="fm-bar-cv" style={{ '--lo': cv.mean - cv.sd, '--hi': cv.mean + cv.sd }} />
              </span>
              <span className="fm-bar-value">
                {f3(held)}
                <span className="fm-bar-cvtext">
                  cross-validated {f3(cv.mean)} ± {f3(cv.sd)}
                </span>
              </span>
            </li>
          )
        })}
      </ul>
      <p className="fm-scale" aria-hidden="true">
        <span>0</span>
        <span>0.5</span>
        <span>1</span>
      </p>
      <p className="fm-key">
        Bar: macro-F1 on the {model.split.held_out_tests} held-out tests. Thin line: mean ± one standard deviation of
        cross-validation on the training days.
      </p>
    </div>
  )
}

function Confusion({ cm }) {
  return (
    <table className="fm-table">
      <caption>Held-out tests, random forest: how each test ended (rows) against what the model gave (columns)</caption>
      <thead>
        <tr>
          <th scope="col">Ended in</th>
          {cm.labels.map((label) => (
            <th key={label} scope="col">
              Given {label.toLowerCase()}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {cm.labels.map((label, i) => (
          <tr key={label}>
            <th scope="row">{label}</th>
            {cm.matrix[i].map((n, j) => (
              <td key={j} className={i === j ? 'fm-diag' : undefined}>
                {n}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  )
}

function PerClass({ perClass, classes }) {
  return (
    <table className="fm-table">
      <caption>Held-out tests, random forest, per outcome</caption>
      <thead>
        <tr>
          <th scope="col">Outcome</th>
          <th scope="col">Tests</th>
          <th scope="col">Precision</th>
          <th scope="col">Recall</th>
          <th scope="col">F1</th>
        </tr>
      </thead>
      <tbody>
        {classes.map((c) => (
          <tr key={c}>
            <th scope="row">{c}</th>
            <td>{perClass[c].tests}</td>
            <td>{f3(perClass[c].precision)}</td>
            <td>{f3(perClass[c].recall)}</td>
            <td>{f3(perClass[c].f1)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

function Shap({ shap, classes, perClass }) {
  const max = Math.max(...classes.flatMap((c) => shap.by_end[c].map((f) => f.mean_abs_shap)))
  return (
    <div className="fm-shap">
      {classes.map((c) => (
        <div key={c} className="fm-shap-group">
          <h5>{c}</h5>
          {perClass[c].recall === 0 && (
            <p className="fm-shap-warn">
              The forest found 0 of the {perClass[c].tests} held-out {c.toLowerCase()}s, so this shows what it leans on,
              not what it gets right.
            </p>
          )}
          <ul>
            {shap.by_end[c].map((f) => (
              <li key={f.feature}>
                <span className="fm-shap-name">{FEATURE_NAMES[f.feature] ?? f.feature}</span>
                <span className="fm-shap-bar" style={{ '--w': f.mean_abs_shap / max }} aria-hidden="true" />
                <span className="fm-shap-value">{f.mean_abs_shap.toFixed(3)}</span>
                <span className="fm-shap-dir">{DIRECTION[f.direction] ?? f.direction}</span>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  )
}

export default function FlexModel() {
  const api = useApi('/flex-model')
  if (api.status === 'loading') return <Loading label="Loading the FLEX model's results…" />
  if (api.status === 'error') return <LoadError what="The FLEX model's results" retry={api.retry} />
  const m = api.data
  const rf = m.held_out[m.chosen_model]
  const chance = m.chance_check

  return (
    <figure className="fixed-figure fm">
      <figcaption>
        <h3>FLEX: what a model found about how tests ended</h3>
        <p>{m.question}</p>
      </figcaption>

      <div className="fm-notice" role="note">
        <Info size={18} aria-hidden="true" />
        <p>{m.notice}</p>
      </div>

      <p className="fm-lead">
        Trained on {m.split.train_tests} tests from {m.split.train_days} test days and scored on {m.split.held_out_tests}{' '}
        tests from {m.split.held_out_days} other days, kept apart by test day, using only what was set before
        each test: fuel, pressure, oxygen, CO₂, helium and droplet diameter. Macro-F1 averages the score of the three
        outcomes, so the rare completions count as much as the common extinctions.
      </p>

      <Scores model={m} />

      <p className="fm-lead">
        The random forest was chosen beforehand for the highest cross-validated score; on the held-out days logistic
        regression scored higher, and the choice was kept. Is the forest better than chance? On the training days, one
        cross-validation pass of the random forest gave {f3(chance.macro_f1)} (the bar's {f3(m.cross_validation.scores[m.chosen_model].mean)} averages
        five passes); trained on outcomes shuffled {chance.shuffles} times it averaged {f3(chance.shuffled_mean)} (best{' '}
        {f3(chance.shuffled_max)}): p = {chance.p_value}, the smallest {chance.shuffles} shuffles can give. This check
        uses the training days, not the held-out tests.
      </p>

      <div className="fm-tables">
        <Confusion cm={rf.confusion_matrix} />
        <PerClass perClass={rf.per_class} classes={m.classes} />
      </div>

      <h4 className="fm-subhead">What the random forest relies on, by outcome</h4>
      <p className="fm-key">
        Mean absolute SHAP value on the held-out tests: how much each condition moves the model's answer. The last
        column says whether a higher value of that condition pushes the answer toward or away from that outcome; mixed
        means it pushes both ways across tests.
      </p>
      <Shap shap={m.shap} classes={m.classes} perClass={rf.per_class} />

      <h4 className="fm-subhead">Limits</h4>
      <ul className="fm-limits">
        {m.limitations.map((line) => (
          <li key={line}>{line}</li>
        ))}
      </ul>

      <p className="footnote">
        Source: <span className="id">backend/data/flex_model/results.json</span>, written by{' '}
        <span className="id">{m.reproduce.command}</span> (seed {m.reproduce.seed}, scikit-learn{' '}
        {m.reproduce.scikit_learn}, shap {m.reproduce.shap}) from {m.data.tests} FLEX tests in{' '}
        <span className="id">{m.source.file}</span>, columns{' '}
        {m.features.map((f) => `“${f.psi_column}”`).join(', ')}. PSI's headings drop subscripts: O is O₂ and CO is
        CO₂.
      </p>
    </figure>
  )
}
