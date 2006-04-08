#include <stdio.h>
#include <stdlib.h>

main()
{
	char	buff[64];
	double	sum = 0.0;

	while (scanf("%s", buff) > 0)
		{
		printf("%s\n", buff);
		sum += atof(buff);
		}

	fprintf(stderr, "sum = %15.8lf\n", sum);
}
