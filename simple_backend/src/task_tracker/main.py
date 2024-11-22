from fastapi import FastAPI, HTTPException
from uuid import UUID, uuid4
from typing import List
from pydantic import BaseModel, Field

app = FastAPI()

class Order:
    TAX_RATE = 0.08  # 8% налог
    SERVICE_CHARGE = 0.05  # 5% сервисный сбор

    def __init__(self, customer):
        self.customer = customer
        self.dishes = []

    def add_dish(self, dish):
        if isinstance(dish, Dish):
            self.dishes.append(dish)
        else:
            raise ValueError("Можно добавлять только объекты класса Dish.")

    def remove_dish(self, dish):
        if dish in self.dishes:
            self.dishes.remove(dish)
        else:
            raise ValueError("Такого блюда нет в заказе.")

    def calculate_total(self):
        return sum(dish.price for dish in self.dishes)

    def final_total(self):
        total_after_discount = self.apply_discount()
        total_with_tax = total_after_discount * (1 + Order.TAX_RATE)
        final_total = total_with_tax * (1 + Order.SERVICE_CHARGE)
        return final_total

    def apply_discount(self):
        discount_rate = self.customer.get_discount() / 100
        return self.calculate_total() * (1 - discount_rate)

    def __str__(self):
        dish_list = "\n".join([str(dish) for dish in self.dishes])
        return f"Order for {self.customer.name}:\n{dish_list}\nTotal: ${self.final_total():.2f}"





class GroupOrder(Order):
    def __init__(self, customers):
        super().__init__(customer=None)  # Групповой заказ не привязан к одному клиенту
        self.customers = customers

    def split_bill(self):
        if not self.customers:
            raise ValueError("Нет клиентов для разделения счета.")
        total = self.final_total()
        return total / len(self.customers)

    def __str__(self):
        customer_list = ", ".join([customer.name for customer in self.customers])
        dish_list = "\n".join([str(dish) for dish in self.dishes])
        return f"Group Order for {customer_list}:\n{dish_list}\nTotal: ${self.final_total():.2f}"


class Dish:
    def __init__(self, name, price, category):
        self.name = name
        self.price = price
        self.category = category

    def __str__(self):
        return f"Dish: {self.name}, Category: {self.category}, Price: ${self.price:.2f}"


class Customer:
    def __init__(self, name, membership="Regular"):
        self.name = name
        self.membership = membership

    def get_discount(self):
        if self.membership == "VIP":
            return 10  # VIP клиенты получают 10% скидки
        return 0  # Обычные клиенты не получают скидки

    def __str__(self):
        return f"Customer: {self.name}, Membership: {self.membership}"

tasks = []

class Task(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str
    status: str = "open"

@app.get("/tasks", response_model=List[Task])
def get_tasks():
    return tasks

@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task: Task):
    tasks.append(task)
    return task

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: UUID, updated_task: Task):
    for i, task in enumerate(tasks):
        if task.id == task_id:
            tasks[i] = updated_task
            return updated_task
    raise HTTPException(status_code=404, detail="Task not found")


@app.delete("/tasks/{task_id}")
def delete_task(task_id: UUID):
    for i, task in enumerate(tasks):
        if task.id == task_id:
            del tasks[i]
            return {"message": "Task deleted"}
    raise HTTPException(status_code=404, detail="Task not found")