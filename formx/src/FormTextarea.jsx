import React from 'react'

const FormTextarea = ({ id, value, onChange, placeholder, rows}) => { // Added value, onChange
  return (
     <textarea
      className="form-textarea w-full rounded-lg border-border-light bg-background-light p-4 text-base font-normal text-text-light placeholder:text-subtle-light/70 focus:border-accent focus:ring-2 focus:ring-accent/30 dark:border-border-dark dark:bg-background-dark dark:text-text-dark dark:placeholder:text-subtle-dark/70"
      id={id}
      name={id}
      placeholder={placeholder}
      rows={rows || 5}
      value={value} // Use passed value
      onChange={onChange} // Use passed onChange
    />
  )
}

export default FormTextarea;