/*
-------------------------------------------------------------------------
OBJECT NAME:	Queue.cc

FULL NAME:	Generic Queue stuff.

ENTRY POINTS:	Queue(), ~Queue()
		EnQueue(data)
		DeQueue()
		Front()

DESCRIPTION:	

INPUT:		

OUTPUT:		

REFERENCES:	none

REFERENCED BY:	none
-------------------------------------------------------------------------
*/

#include "Queue.h"

#include <cstdio>

/* -------------------------------------------------------------------- */
Queue::Queue()
{
  head = tail = (QueueNode *)NULL;

}	/* END CREATEQUEUE */

/* -------------------------------------------------------------------- */
Queue::~Queue()
{
  QueueNode	*trace, *tmp;

  for (trace = head; trace; )
    {
    tmp = trace;
    trace = trace->next;
    delete tmp;
    }

}	/* END DESTROYQUEUE */

/* -------------------------------------------------------------------- */
bool Queue::EnQueue(void *data)
{
  QueueNode	*tmp;

  if (data == NULL)
    return(false);

  tmp = new QueueNode;

  tmp->data = data;
  tmp->next = (QueueNode *)NULL;

  if (head == NULL)
    head = tail = tmp;
  else
    {
    tail->next = tmp;
    tail = tmp;
    }

  return(true);

}	/* END ENQUEUE */

/* -------------------------------------------------------------------- */
void *Queue::DeQueue()
{
  QueueNode	*tmp;
  void		*tmpDat;

  if (head == (QueueNode *)NULL)
    return(NULL);

  tmp	= head;
  head	= tmp->next;

  if (head == (QueueNode *)NULL)
    tail = (QueueNode *)NULL;

  tmpDat = tmp->data;
  delete tmp;

  return(tmpDat);

}	/* END DEQUEUE */

/* END QUEUE.C */
