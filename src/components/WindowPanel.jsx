function WindowPanel({ title, children }) {
  return (
    <div className="panel">

      <div className="panel-title">
        {title}
      </div>

      <div className="panel-content">
        {children}
      </div>

    </div>
  )
}

export default WindowPanel