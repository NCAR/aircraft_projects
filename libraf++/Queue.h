/*
-------------------------------------------------------------------------
OBJECT NAME:	queue.h

FULL NAME:	Header file for Queue
-------------------------------------------------------------------------
*/

#ifndef QUEUE_H
#define QUEUE_H

#ifndef NULL
#define NULL	((void *)0)
#endif


class Queue
{
public:
	Queue();
	~Queue();

  bool	EnQueue(void *);
  void	*DeQueue();
  void	*Front()	{ return(head ? head->data : NULL); }


private:
	typedef struct qnode
		{
		struct qnode	*next;
		void		*data;
		} QueueNode;


  QueueNode	*head;
  QueueNode	*tail;

};

#endif
