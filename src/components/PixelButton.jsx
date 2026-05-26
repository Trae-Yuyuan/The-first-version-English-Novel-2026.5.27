function PixelButton({ text, onClick }) {
  return (
    <button
      className="pixel-btn"
      onClick={onClick}
    >
      {text}
    </button>
  )
}

export default PixelButton