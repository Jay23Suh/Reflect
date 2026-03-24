import { useState, useEffect } from 'react'
import { ReactComponent as LegoIcon } from './lego.svg'

export default function Intro({ onDone }) {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const t = setTimeout(() => setVisible(true), 60)
    return () => clearTimeout(t)
  }, [])

  function handleBegin() {
    localStorage.setItem('ground_intro_seen', '1')
    onDone()
  }

  return (
    <div className={`intro-overlay${visible ? ' intro-visible' : ''}`}>
      <div className="intro-content">
        <LegoIcon className="intro-icon" />
        <p className="intro-line intro-line--1">we are all busy with something.</p>
        <p className="intro-line intro-line--2">it's important to ground ourselves —</p>
        <p className="intro-line intro-line--3">be grateful. be present.</p>
        <p className="intro-line intro-line--4">get to know yourself.</p>
        <button className="intro-btn" onClick={handleBegin}>let's begin</button>
      </div>
    </div>
  )
}
