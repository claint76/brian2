from base import Language

__all__ = ['PythonLanguage']

class PythonLanguage(Language):
    
    def translate_expression(self, expr):
        return expr.strip()
    
    def translate_statement(self, statement):
        # TODO: optimisation, translate arithmetic to a sequence of inplace
        # operations like a=b+c -> add(b, c, a)
        var, op, expr = statement.var, statement.op, statement.expr
        if op==':=':
            op = '='
        return var+' '+op+' '+self.translate_expression(expr)

    def translate_statement_sequence(self, statements, specifiers,
                                     index_var, index_spec):
        read, write = self.array_read_write(statements, specifiers)
        lines = []
        # read arrays
        for var in read:
            line = var+' = '+specifiers[var].array
            if not index_spec.all:
                line = line+'['+index_var+']'
            lines.append(line)
        # the actual code
        lines.extend([self.translate_statement(stmt) for stmt in statements])
        # write arrays
        # TODO: optimisation, if we have never done var = expr but always
        # var += expr or things like that, AND if we are iterating over the
        # whole array, then we do not need to do this final write of the
        # variable, and this is a common use-case in state update code.
        for var in write:
            line = specifiers[var].array
            if index_spec.all:
                line = line+'[:]'
            else:
                line = line+'['+index_var+']'
            line = line+' = '+var
            lines.append(line)
        return '\n'.join(lines)

    def template_iterate_all(self, index, size):
        return '''
        %CODE%
        '''
    
    def template_iterate_index_array(self, index, array, size):
        return '''
        {index} = {array}
        %CODE%
        '''.format(index=index, array=array)

    def template_threshold(self):
        return '''
        %CODE%
        return _cond.nonzero()[0]
        '''
