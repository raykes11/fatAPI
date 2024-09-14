from fastapi import APIRouter, Depends, status, HTTPException
from app.backend.db import Base
from sqlalchemy import Column,Integer,String,Boolean,ForeignKey
from sqlalchemy.orm import relationship,Session
from sqlalchemy.schema import CreateTable
from app.backend.db_depends import get_db
from typing import Annotated
from app.schemas import CreateTask, UpdateTask
from sqlalchemy import insert, select, update, delete
from slugify import slugify
from app.moduls.task import Task
from app.moduls.user import User

router = APIRouter(prefix='/task', tags=['task'])


@router.get('/')
async def all_tasks(db: Annotated[Session, Depends(get_db)]):
    task = db.scalars(select(Task)).all()
    return task


@router.get('/task_id')
async def task_by_id(db: Annotated[Session, Depends(get_db)],task_id: int):
    task = db.scalars(select(Task).where(Task.id == task_id)).fetchall()
    if task == []:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Task was not found'
        )
    return task



@router.post('/create')
async def create_task(db: Annotated[Session, Depends(get_db)], user_id: int, create_task: CreateTask):
    task = db.scalars(select(Task).where(Task.title == create_task.title)).fetchall()
    user = db.scalars(select(User).where(User.id == user_id)).fetchall()
    if task != []:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail='This task name is create'
        )
    if user == []:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no category found'
        )
    db.execute(insert(Task).values(title=create_task.title,
                                   content=create_task.content,
                                   priority=create_task.priority,
                                   completed=False,
                                   user_id=user_id,
                                   slug=slugify(create_task.title)))
    db.commit()
    return {
        "status_code": status.HTTP_201_CREATED,
        "transaction": 'Successful'
    }


@router.put('/update')
async def update_task(db: Annotated[Session, Depends(get_db)],task_id: int,update_task:UpdateTask):
    task = db.scalars(select(Task).where(Task.id == task_id)).fetchall()
    if task == []:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User was not found'
        )
    db.execute(update(Task).where(Task.id == task_id).values(title=update_task.title,
                                   content=update_task.content,
                                   priority=update_task.priority,
                                   completed=False,
                                   slug=slugify(update_task.title)))
    db.commit()
    return {
        "status_code": status.HTTP_200_OK,
        "transaction": 'Successful'
    }


@router.delete('/delete')
async def delete_task(db: Annotated[Session, Depends(get_db)],task_id: int):
    task = db.scalars(select(Task).where(Task.id == task_id)).fetchall()
    if task == []:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User was not found'
        )
    db.execute(delete(Task).where(Task.id == task_id))
    db.commit()
    return {
        "status_code": status.HTTP_200_OK,
        "transaction": 'Successful'
    }

