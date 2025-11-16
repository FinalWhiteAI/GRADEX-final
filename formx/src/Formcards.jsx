import React from 'react'

const Formcards = ({children}) => {
  return (
   <div className="rounded-xl bg-card-light p-6 shadow-soft dark:bg-card-dark dark:shadow-soft-dark">
      {children}
    </div>
  )
}

export default Formcards