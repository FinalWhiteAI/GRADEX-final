import React from 'react'

const FormInput = ({ id, value, onChange, placeholder }) => { // Added value, onChange
  return (
    <input
      className="form-input h-14 w-full rounded-lg border-border-light bg-background-light p-4 text-base font-normal text-text-light placeholder:text-subtle-light/70 focus:border-accent focus:ring-2 focus:ring-accent/30 dark:border-border-dark dark:bg-background-dark dark:text-text-dark dark:placeholder:text-subtle-dark/70"
      id={id}
      name={id}
      placeholder={placeholder || "Please Enter"} // Use passed placeholder
      type="text"
      value={value} // Use passed value
      onChange={onChange} // Use passed onChange
    />
  )
}

export default FormInput