import { defineStore } from 'pinia'

export const useTodoStore = defineStore('todo', {
  state: () => ({
    count: 0,
    title: "Cook noodles",
    done: false
  }),
  actions: {
    increment() {
      this.count++
    }
  }
})
