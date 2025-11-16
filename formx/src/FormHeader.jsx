import React from 'react'

const FormHeader = (props) => {
  return (
     <header className="sticky top-0 z-10 bg-background-light/80 py-4 backdrop-blur-sm dark:bg-background-dark/80">
      <div className="relative mx-auto flex w-full max-w-2xl items-center justify-between px-4">
        <button className="flex size-10 items-center justify-center rounded-full text-text-light dark:text-text-dark">
          <span className="material-symbols-outlined">arrow_back</span>
        </button>
        <h1 className="text-lg font-bold text-text-light dark:text-text-dark font-serif">{props.title}</h1>
        <div className="size-10"></div>
      </div>
    </header>
  )
}

export default FormHeader