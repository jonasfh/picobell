<?php

declare(strict_types=1);

use Phinx\Migration\AbstractMigration;

final class ApiLogTable extends AbstractMigration
{
    /**
     * Change Method.
     *
     * Write your reversible migrations using this method.
     *
     * More information on writing migrations is available here:
     * https://book.cakephp.org/phinx/0/en/migrations.html#the-change-method
     *
     * Remember to call "create()" or "update()" and NOT "save()" when working
     * with the Table class.
     */
    public function change(): void
    {
        // === API LOG ===
        $this->table('api_log')
            ->addColumn('method', 'string', [
                'limit' => 10,
                'null' => true,
            ])
            ->addColumn('endpoint', 'string', [
                'limit' => 255,
                'null' => true,
            ])
            ->addColumn('ip', 'string', [
                'limit' => 64,
                'null' => true,
            ])
            ->addColumn('email', 'string', [
                'limit' => 255,
                'null' => true,
            ])
            ->addColumn('payload', 'text', [
                'null' => true,
            ])
            ->addColumn('created_at', 'datetime', [
                'default' => 'CURRENT_TIMESTAMP',
            ])
            ->create();
    }
}
