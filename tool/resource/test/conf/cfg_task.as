

package conf
{
    import manager.ConfigManager;

	public class cfg_task
	{
        public static function init(sheet:Object):cfg_task
        {
            var a:cfg_task = new cfg_task();

            
            a.worldcup_item_nums=sheet[0];
            
            a.activity_item_ids=sheet[1];
            
            a.worldcup_item_ids=sheet[2];
            
            a.id=sheet[3];
            
            a.activity_item_nums=sheet[4];
            

			return a;
        }
        public static function instance(key:Object):cfg_task
		{
            return ConfigManager.getConfObject("cfg_task",key) as cfg_task;
		}


        
        public var worldcup_item_nums:Array;
        
        public var activity_item_ids:Array;
        
        public var worldcup_item_ids:Array;
        
        public var id:int;
        
        public var activity_item_nums:Array;
        






	}
}