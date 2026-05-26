import { useDropzone } from 'react-dropzone'

function DropZone({ text, onFileDrop }) {

  const { getRootProps, getInputProps } = useDropzone({
    onDrop: acceptedFiles => {

      const file = acceptedFiles[0]

      if (file) {
        onFileDrop(file)
      }
    }
  })

  return (

    <div
      {...getRootProps()}
      className="drop-zone"
    >

      <input {...getInputProps()} />

      <p>{text}</p>

    </div>
  )
}

export default DropZone