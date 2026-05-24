import { useState, useEffect } from 'react'
import './App.css'
import Sidebar    from './components/Sidebar'
import Upload     from './steps/Upload'
import PolicyCheck from './steps/PolicyCheck'
import Checkpoint  from './steps/Checkpoint'
import MarketIntel from './steps/MarketIntel'
import Questions   from './steps/Questions'
import Memo        from './steps/Memo'
import Report      from './steps/Report'
import Rejected    from './steps/Rejected'

const INIT = {
  step:          1,
  startup:       null,
  policyResult:  null,
  humanDecision: null,
  analystNotes:  '',
  marketIntel:   null,
  questions:     null,
  memo:          null,
}

export default function App() {
  const [state, setState]   = useState(INIT)
  const [health, setHealth] = useState(null)

  const set = (patch) => setState(s => ({ ...s, ...patch }))

  useEffect(() => {
    fetch('/api/health')
      .then(r => r.json())
      .then(setHealth)
      .catch(() => {})
  }, [])

  const restart = () => setState(INIT)

  const { step, startup, policyResult, analystNotes, marketIntel, questions, memo } = state

  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <Upload
            onDone={s => set({ startup: s, step: 2 })}
          />
        )
      case 2:
        return (
          <PolicyCheck
            startup={startup}
            onDone={pr => set({ policyResult: pr, step: 3 })}
            onBack={() => set({ step: 1, startup: null })}
          />
        )
      case 3:
        return (
          <Checkpoint
            startup={startup}
            policyResult={policyResult}
            onApprove={notes => set({ humanDecision: 'approved', analystNotes: notes, step: 4 })}
            onReject={notes  => set({ humanDecision: 'rejected', analystNotes: notes, step: 99 })}
            onBack={() => set({ step: 2 })}
          />
        )
      case 4:
        return (
          <MarketIntel
            startup={startup}
            policyResult={policyResult}
            analystNotes={analystNotes}
            onDone={intel => set({ marketIntel: intel, step: 5 })}
            onBack={() => set({ step: 3, marketIntel: null })}
          />
        )
      case 5:
        return (
          <Questions
            startup={startup}
            policyResult={policyResult}
            marketIntel={marketIntel}
            onDone={qs => set({ questions: qs, step: 6 })}
            onBack={() => set({ step: 4, questions: null })}
          />
        )
      case 6:
        return (
          <Memo
            startup={startup}
            policyResult={policyResult}
            marketIntel={marketIntel}
            questions={questions}
            onDone={m => set({ memo: m, step: 7 })}
            onBack={() => set({ step: 5, memo: null })}
          />
        )
      case 7:
        return (
          <Report
            startup={startup}
            policyResult={policyResult}
            marketIntel={marketIntel}
            questions={questions}
            memo={memo}
            analystNotes={analystNotes}
            onBack={() => set({ step: 6, memo: null })}
            onRestart={restart}
          />
        )
      case 99:
        return (
          <Rejected
            startup={startup}
            policyResult={policyResult}
            analystNotes={analystNotes}
            onRestart={restart}
          />
        )
      default:
        return null
    }
  }

  const sidebarStep = step === 99 ? 3 : step

  return (
    <div className="app-shell">
      <Sidebar step={sidebarStep} health={health} />
      <main className="main-content">
        {renderStep()}
      </main>
    </div>
  )
}
