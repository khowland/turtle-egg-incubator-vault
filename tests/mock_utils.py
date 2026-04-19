from unittest.mock import MagicMock

def build_table_aware_mock(table_data_map):
    """
    Creates a mock Supabase client where .table(name) returns a mock
    that is pre-configured with the data in table_data_map[name].
    """
    mock_supabase = MagicMock()
    table_mocks = {}
    
    def get_table_mock(name):
        if name in table_mocks:
            return table_mocks[name]
        
        tm = MagicMock()
        data = table_data_map.get(name, [])
        
        # Configure the chainable mock
        # .select().eq().order().limit().execute().data
        select_mock = tm.select.return_value
        eq_mock = select_mock.eq.return_value
        order_mock = eq_mock.order.return_value
        limit_mock = order_mock.limit.return_value
        
        # Mock .execute().data
        exec_mock = MagicMock()
        exec_mock.data = data
        
        # Make all points in the chain return a mock that has .execute()
        select_mock.execute.return_value = exec_mock
        eq_mock.execute.return_value = exec_mock
        order_mock.execute.return_value = exec_mock
        limit_mock.execute.return_value = exec_mock
        
        # Special case for .eq().eq()
        eq_mock.eq.return_value.execute.return_value = exec_mock
        
        table_mocks[name] = tm
        return tm
        
    mock_supabase.table.side_effect = get_table_mock
    return mock_supabase, table_mocks
